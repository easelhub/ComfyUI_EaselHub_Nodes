import os
import torch
import folder_paths
from PIL import Image
from transformers import AutoProcessor, AutoModelForCausalLM
from modelscope.hub.snapshot_download import snapshot_download

class EHN_Florence2PromptGen:
    def __init__(self):
        self.model = None
        self.processor = None
        self.current_model_path = None

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "model_version": (["Florence-2-large-PromptGen-v2.0", "Florence-2-base-PromptGen-v2.0"],),
                "task": (["<MORE_DETAILED_CAPTION>", "<DETAILED_CAPTION>", "<CAPTION>", "<GENERATE_TAGS>", "<MIXED_CAPTION>"],),
            },
            "optional": {
                "text_input": ("STRING", {"multiline": True}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "generate"
    CATEGORY = "EaselHub Nodes/AI"

    def generate(self, image, model_version, task, text_input=""):
        model_id = f"cutemodel/{model_version}"
        models_dir = os.path.join(folder_paths.models_dir, "Florence-2")
        model_path = os.path.join(models_dir, model_version)

        if not os.path.exists(model_path):
            print(f"Downloading {model_version} to {model_path}...")
            snapshot_download(model_id, cache_dir=models_dir, local_dir=model_path)

        device = "cuda" if torch.cuda.is_available() else "cpu"
        dtype = torch.float16 if device == "cuda" else torch.float32

        if self.model is None or self.current_model_path != model_path:
            self.model = AutoModelForCausalLM.from_pretrained(model_path, torch_dtype=dtype, trust_remote_code=True).to(device)
            self.processor = AutoProcessor.from_pretrained(model_path, trust_remote_code=True)
            self.current_model_path = model_path

        pil_image = Image.fromarray((image[0].cpu().numpy() * 255).astype("uint8"))
        
        prompt = task
        if text_input:
            prompt = task + text_input

        inputs = self.processor(text=prompt, images=pil_image, return_tensors="pt").to(device, dtype)

        # 智能参数配置
        gen_kwargs = {
            "input_ids": inputs["input_ids"],
            "pixel_values": inputs["pixel_values"],
            "max_new_tokens": 1024,
            "num_beams": 3,
            "do_sample": False,
            "repetition_penalty": 1.05,
        }

        # 针对不同任务微调参数
        if task == "<GENERATE_TAGS>":
            gen_kwargs["max_new_tokens"] = 512
            gen_kwargs["repetition_penalty"] = 1.1 # 标签生成更需要避免重复
        elif task == "<MORE_DETAILED_CAPTION>":
            gen_kwargs["max_new_tokens"] = 2048 # 详细描述需要更长文本
        elif task == "<MIXED_CAPTION>":
             gen_kwargs["do_sample"] = True # 混合模式增加一点随机性可能更好
             gen_kwargs["temperature"] = 0.7
             gen_kwargs["top_p"] = 0.9

        generated_ids = self.model.generate(**gen_kwargs)

        generated_text = self.processor.batch_decode(generated_ids, skip_special_tokens=False)[0]
        parsed_answer = self.processor.post_process_generation(generated_text, task=task, image_size=(pil_image.width, pil_image.height))
        
        return (str(parsed_answer[task]),)
