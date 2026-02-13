import os
import torch
from PIL import Image
from unittest.mock import patch
from transformers.dynamic_module_utils import get_imports
import torchvision.transforms.functional as F
from torchvision import transforms
from transformers import AutoModelForCausalLM, AutoProcessor
import comfy.model_management as mm
from comfy.utils import ProgressBar
import folder_paths
import random
import string

def fixed_get_imports(filename: str | os.PathLike) -> list[str]:
    if not str(filename).endswith("modeling_florence2.py"):
        return get_imports(filename)
    imports = get_imports(filename)
    try:
        imports.remove("flash_attn")
    except:
        pass
    return imports

class EHN_Florence2Tagger:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "model": (['Florence-2-large-PromptGen-v2.0', 'Florence-2-base-PromptGen-v2.0'], {"default": "Florence-2-large-PromptGen-v2.0"}),
                "image": ("IMAGE",),
                "caption_method": (['tags', 'simple', 'detailed', 'extra', 'mixed', 'extra_mixed', 'analyze'], {"default": "extra_mixed"}),
                "max_new_tokens": ("INT", {"default": 1024, "min": 1, "max": 4096}),
                "num_beams": ("INT", {"default": 3, "min": 1, "max": 64}),
                "random_prompt": (['never', 'always'], {"default": "never"})
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("caption",)
    FUNCTION = "tag_image"
    CATEGORY = "EaselHub/Tagger"

    def tag_image(self, model, image, caption_method, max_new_tokens, num_beams, random_prompt):
        device = mm.get_torch_device()
        dtype = {"bf16": torch.bfloat16, "fp16": torch.float16, "fp32": torch.float32}['fp16']
        model_path = os.path.join(folder_paths.models_dir, "Florence-2", model)
        
        required_files = ["config.json", "pytorch_model.bin", "model.safetensors"]
        if not os.path.exists(model_path) or not any(os.path.exists(os.path.join(model_path, f)) for f in required_files[1:]):
            from huggingface_hub import snapshot_download
            repo_id = f"MiaoshouAI/{model}"
            snapshot_download(repo_id=repo_id, local_dir=model_path, local_dir_use_symlinks=False)

        with patch("transformers.dynamic_module_utils.get_imports", fixed_get_imports):
            model_obj = AutoModelForCausalLM.from_pretrained(model_path, attn_implementation='sdpa', device_map=device, torch_dtype=dtype, trust_remote_code=True).to(device)
        
        processor = AutoProcessor.from_pretrained(model_path, trust_remote_code=True)
        
        to_pil = transforms.ToPILImage()
        pil_images = []
        if image.ndim == 4:
            for i in range(image.shape[0]):
                pil_images.append(to_pil(image[i].permute(2, 0, 1)))
        else:
             pil_images.append(to_pil(image.permute(2, 0, 1)))

        captions = []
        pbar = ProgressBar(len(pil_images))
        do_sample = True if random_prompt == 'always' else False
        
        prompts = {
            'tags': "<GENERATE_TAGS>",
            'simple': "<CAPTION>",
            'detailed': "<DETAILED_CAPTION>",
            'extra': "<MORE_DETAILED_CAPTION>",
            'mixed': "<MIX_CAPTION>",
            'extra_mixed': "<MIX_CAPTION_PLUS>",
            'analyze': "<ANALYZE>"
        }
        prompt = prompts.get(caption_method, "<ANALYZE>")

        for img in pil_images:
            inputs = processor(text=prompt, images=img, return_tensors="pt", do_rescale=False).to(dtype).to(device)
            generated_ids = model_obj.generate(
                input_ids=inputs["input_ids"],
                pixel_values=inputs["pixel_values"],
                max_new_tokens=max_new_tokens,
                early_stopping=False,
                do_sample=do_sample,
                num_beams=num_beams,
            )
            generated_text = processor.batch_decode(generated_ids, skip_special_tokens=False)[0]
            parsed_answer = processor.post_process_generation(generated_text, task=prompt, image_size=(img.width, img.height))
            tags = parsed_answer[prompt]
            
            captions.append(tags)
            pbar.update(1)

        return (", ".join(captions),)

    @classmethod
    def IS_CHANGED(s, model, image, caption_method, max_new_tokens, num_beams, random_prompt):
        if random_prompt == 'always':
            return ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        return ''
