import os
import torch
import folder_paths
import numpy as np
import pandas as pd
from PIL import Image
from modelscope.hub.snapshot_download import snapshot_download
from onnxruntime import InferenceSession

class EHN_WD14Tagger:
    def __init__(self):
        self.session = None
        self.current_model = None

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "model": (["wd-v1-4-moat-tagger-v2", "wd-v1-4-convnext-tagger-v2", "wd-v1-4-swinv2-tagger-v2", "wd-v1-4-vit-tagger-v2"],),
                "threshold": ("FLOAT", {"default": 0.35, "min": 0.0, "max": 1.0, "step": 0.05}),
                "character_threshold": ("FLOAT", {"default": 0.85, "min": 0.0, "max": 1.0, "step": 0.05}),
                "exclude_tags": ("STRING", {"default": ""}),
            }
        }
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("tags",)
    FUNCTION = "tag"
    CATEGORY = "EaselHub Nodes/AI"

    def tag(self, image, model, threshold, character_threshold, exclude_tags):
        models_dir = os.path.join(folder_paths.models_dir, "WD14")
        model_path = os.path.join(models_dir, model, "model.onnx")
        csv_path = os.path.join(models_dir, model, "selected_tags.csv")
        
        if not os.path.exists(model_path) or not os.path.exists(csv_path):
            snapshot_download(f"fireicewolf/{model}", cache_dir=models_dir, local_dir=os.path.join(models_dir, model))

        if self.session is None or self.current_model != model:
            self.session = InferenceSession(model_path, providers=['CUDAExecutionProvider', 'CPUExecutionProvider'])
            self.current_model = model
            self.tags_df = pd.read_csv(csv_path)

        img = Image.fromarray((image[0].cpu().numpy() * 255).astype("uint8")).convert("RGB")
        size = 448
        img = img.resize((size, size), Image.BICUBIC)
        
        img_input = np.array(img).astype(np.float32)
        img_input = img_input[:, :, ::-1] 
        img_input = np.expand_dims(img_input, 0)

        input_name = self.session.get_inputs()[0].name
        label_name = self.session.get_outputs()[0].name
        probs = self.session.run([label_name], {input_name: img_input})[0][0]

        tags = self.tags_df
        general_tags = tags[tags['category'] == 0]
        character_tags = tags[tags['category'] == 4]

        general_res = general_tags[probs[general_tags.index] > threshold]
        character_res = character_tags[probs[character_tags.index] > character_threshold]

        res_tags = dict(zip(general_res['name'], probs[general_res.index]))
        res_tags.update(dict(zip(character_res['name'], probs[character_res.index])))

        exclude = [t.strip() for t in exclude_tags.split(",") if t.strip()]
        final_tags = [t for t, p in sorted(res_tags.items(), key=lambda x: x[1], reverse=True) if t not in exclude]
        
        return (", ".join(final_tags).replace("_", " "),)