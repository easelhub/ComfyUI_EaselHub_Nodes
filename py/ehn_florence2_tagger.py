import os, torch, random, string, shutil, folder_paths
import comfy.model_management as mm
from PIL import Image
from unittest.mock import patch
from transformers.dynamic_module_utils import get_imports
from transformers import AutoModelForCausalLM, AutoProcessor

def fgi(f): return [x for x in get_imports(f) if x != "flash_attn"] if str(f).endswith("modeling_florence2.py") else get_imports(f)

class EHN_Florence2Tagger:
    CATEGORY, RETURN_TYPES, RETURN_NAMES, FUNCTION = "EaselHub/Tagger", ("STRING",), ("caption",), "tag"
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "model": (['Florence-2-large-PromptGen-v2.0', 'Florence-2-base-PromptGen-v2.0'], {"default": "Florence-2-large-PromptGen-v2.0"}),
            "image": ("IMAGE",),
            "method": (['tags', 'simple', 'detailed', 'extra', 'mixed', 'extra_mixed'], {"default": "extra_mixed"}),
            "max_tokens": ("INT", {"default": 1024, "min": 1, "max": 4096}),
        }, "optional": {"random": ("BOOLEAN", {"default": False})}}

    def tag(self, model, image, method, max_tokens, random=False):
        dev, dtype = mm.get_torch_device(), torch.float16 if mm.should_use_fp16() else torch.float32
        mp = os.path.join(folder_paths.models_dir, "Florence-2", model)
        if not os.path.exists(mp) or not os.listdir(mp):
            try:
                from modelscope.hub.snapshot_download import snapshot_download
                snapshot_download(f"cutemodel/{model}", local_dir=mp)
            except:
                from huggingface_hub import snapshot_download
                snapshot_download(repo_id=f"MiaoshouAI/{model}", local_dir=mp)
        
        with patch("transformers.dynamic_module_utils.get_imports", fgi):
            m = AutoModelForCausalLM.from_pretrained(mp, attn_implementation='sdpa', device_map=dev, torch_dtype=dtype, trust_remote_code=True).eval()
        p = AutoProcessor.from_pretrained(mp, trust_remote_code=True)
        
        task_prompts = {"tags": "<GENERATE_TAGS>", "simple": "<CAPTION>", "detailed": "<DETAILED_CAPTION>", "extra": "<MORE_DETAILED_CAPTION>", "mixed": "<MIX_CAPTION>", "extra_mixed": "<MIX_CAPTION_PLUS>"}
        pmt = task_prompts.get(method, "<GENERATE_TAGS>")
        
        res = []
        for img_tensor in image:
            img = Image.fromarray((img_tensor.cpu().numpy() * 255).astype('uint8'))
            inputs = p(text=pmt, images=img, return_tensors="pt").to(dev, dtype)
            with torch.no_grad():
                out = m.generate(input_ids=inputs["input_ids"], pixel_values=inputs["pixel_values"], max_new_tokens=max_tokens, do_sample=random, num_beams=3 if not random else 1)
            generated_text = p.batch_decode(out, skip_special_tokens=False)[0]
            parsed_answer = p.post_process_generation(generated_text, task=pmt, image_size=img.size)
            res.append(parsed_answer[pmt] if pmt in parsed_answer else generated_text)
            
        return (", ".join(res),)
