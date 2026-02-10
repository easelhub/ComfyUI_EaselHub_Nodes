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
                "model": (["Florence-2-large-PromptGen-v2.0", "Florence-2-base-PromptGen-v2.0"], {"default": "Florence-2-large-PromptGen-v2.0"}),
                "caption_method": (["extra_mixed", "mixed", "detailed", "simple", "tags", "extra", "analyze"], {"default": "extra_mixed"}),
                "max_new_tokens": ("INT", {"default": 1024, "min": 1, "max": 4096}),
                "num_beams": ("INT", {"default": 4, "min": 1, "max": 64}),
                "random_prompt": (["never", "always"], {"default": "never"}),
            }
        }
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "generate"
    CATEGORY = "EaselHub Nodes/AI"

    def generate(self, image, model, caption_method, max_new_tokens, num_beams, random_prompt):
        model_id = f"cutemodel/{model}"
        models_dir = os.path.join(folder_paths.models_dir, "Florence-2")
        model_path = os.path.join(models_dir, model)
        if not os.path.exists(model_path): snapshot_download(model_id, cache_dir=models_dir, local_dir=model_path)
        device = "cuda" if torch.cuda.is_available() else "cpu"
        dtype = torch.float16 if device == "cuda" else torch.float32
        if self.model is None or self.current_model_path != model_path:
            self.model = AutoModelForCausalLM.from_pretrained(model_path, torch_dtype=dtype, trust_remote_code=True).to(device)
            self.processor = AutoProcessor.from_pretrained(model_path, trust_remote_code=True)
            self.current_model_path = model_path
        
        prompt_map = {
            "tags": "<GENERATE_TAGS>",
            "simple": "<CAPTION>",
            "detailed": "<DETAILED_CAPTION>",
            "extra": "<MORE_DETAILED_CAPTION>",
            "mixed": "<MIX_CAPTION>",
            "extra_mixed": "<MIX_CAPTION_PLUS>",
            "analyze": "<ANALYZE>"
        }
        task = prompt_map.get(caption_method, "<MIX_CAPTION_PLUS>")
        
        pil_image = Image.fromarray((image[0].cpu().numpy() * 255).astype("uint8"))
        inputs = self.processor(text=task, images=pil_image, return_tensors="pt").to(device, dtype)
        gen_kwargs = {
            "input_ids": inputs["input_ids"],
            "pixel_values": inputs["pixel_values"],
            "max_new_tokens": max_new_tokens,
            "num_beams": num_beams,
            "do_sample": True if random_prompt == "always" else False,
            "repetition_penalty": 1.05,
        }
        generated_ids = self.model.generate(**gen_kwargs)
        generated_text = self.processor.batch_decode(generated_ids, skip_special_tokens=False)[0]
        parsed_answer = self.processor.post_process_generation(generated_text, task=task, image_size=(pil_image.width, pil_image.height))
        return (str(parsed_answer[task]),)