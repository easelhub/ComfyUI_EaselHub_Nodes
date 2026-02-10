import os
import csv
import numpy as np
import onnxruntime as ort
from PIL import Image
import folder_paths
from modelscope.hub.snapshot_download import snapshot_download

class EHN_WD14Tagger:
    def __init__(self):
        self.ort_sess = None
        self.model_name = None
        self.tags = []

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "model": ([
                    "wd-v1-4-moat-tagger-v2",
                    "wd-v1-4-convnext-tagger-v2",
                    "wd-v1-4-swinv2-tagger-v2",
                    "wd-v1-4-vit-tagger-v2",
                    "wd-vit-tagger-v3",
                    "wd-swinv2-tagger-v3",
                    "wd-convnext-tagger-v3"
                ],),
                "threshold": ("FLOAT", {"default": 0.35, "min": 0.0, "max": 1.0, "step": 0.05}),
                "character_threshold": ("FLOAT", {"default": 0.85, "min": 0.0, "max": 1.0, "step": 0.05}),
                "replace_underscore": ("BOOLEAN", {"default": True}),
                "trailing_comma": ("BOOLEAN", {"default": False}),
                "exclude_tags": ("STRING", {"default": "", "multiline": True}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("tags",)
    FUNCTION = "tag"
    CATEGORY = "EaselHub Nodes/AI"

    def tag(self, image, model, threshold, character_threshold, replace_underscore, trailing_comma, exclude_tags):
        mdir = os.path.join(folder_paths.models_dir, "WD14")
        mpath = os.path.join(mdir, model, "model.onnx")
        cpath = os.path.join(mdir, model, "selected_tags.csv")

        if not os.path.exists(mpath) or not os.path.exists(cpath):
            snapshot_download(f"fireicewolf/{model}", cache_dir=mdir, local_dir=os.path.join(mdir, model))

        if self.model_name != model:
            self.ort_sess = ort.InferenceSession(mpath, providers=['CUDAExecutionProvider', 'CPUExecutionProvider'])
            self.model_name = model
            with open(cpath, 'r', encoding='utf-8') as f:
                self.tags = list(csv.DictReader(f))

        img = Image.fromarray((image[0].cpu().numpy() * 255).astype("uint8")).convert("RGB")
        size = 448
        img = img.resize((size, size), Image.BICUBIC)
        
        input_data = np.array(img).astype(np.float32)
        input_data = input_data[:, :, ::-1]
        input_data = np.expand_dims(input_data, 0)
        
        input_name = self.ort_sess.get_inputs()[0].name
        probs = self.ort_sess.run([self.ort_sess.get_outputs()[0].name], {input_name: input_data})[0][0]

        res = {}
        for i, tag in enumerate(self.tags):
            p = probs[i]
            cat = tag.get('category')
            if cat == '0':
                if p > threshold: res[tag['name']] = p
            elif cat == '4':
                if p > character_threshold: res[tag['name']] = p

        excl = {t.strip() for t in exclude_tags.split(",") if t.strip()}
        final = [k for k, v in sorted(res.items(), key=lambda x: x[1], reverse=True) if k not in excl]
        
        text = ", ".join(final)
        if replace_underscore: text = text.replace("_", " ")
        if trailing_comma: text += ","
        
        return (text,)