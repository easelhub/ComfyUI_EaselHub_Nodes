import os, torch, folder_paths, shutil
from PIL import Image
from transformers import AutoModelForCausalLM, AutoProcessor
from unittest.mock import patch
from transformers.dynamic_module_utils import get_imports
import comfy.model_management as mm

def fgi(f): return [x for x in get_imports(f) if x != "flash_attn"] if str(f).endswith("modeling_florence2.py") else get_imports(f)

class EHN_Florence2Tagger:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "image": ("IMAGE",),
            "model": (["Florence-2-large-PromptGen-v2.0", "Florence-2-base-PromptGen-v2.0"], {"default": "Florence-2-large-PromptGen-v2.0"}),
            "task": (["MIX_CAPTION_PLUS", "MIX_CAPTION", "MORE_DETAILED_CAPTION", "DETAILED_CAPTION", "CAPTION", "GENERATE_TAGS"], {"default": "MIX_CAPTION_PLUS"}),
            "max_tokens": ("INT", {"default": 1024, "min": 64, "max": 4096}),
            "num_beams": ("INT", {"default": 3, "min": 1, "max": 64}),
            "do_sample": ("BOOLEAN", {"default": False}),
        }}
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("caption",)
    FUNCTION = "execute"
    CATEGORY = "EaselHub/Tagger"
    
    def execute(self, image, model, task, max_tokens, num_beams, do_sample):
        dev = mm.get_torch_device()
        dt = torch.float16 if mm.should_use_fp16() else torch.float32
        mp = os.path.join(folder_paths.models_dir, "LLM", model)
        if not os.path.exists(mp) or not os.listdir(mp):
            if os.path.exists(mp): shutil.rmtree(mp)
            from huggingface_hub import snapshot_download
            snapshot_download(repo_id=f"MiaoshouAI/{model}", local_dir=mp)
        with patch("transformers.dynamic_module_utils.get_imports", fgi):
            try:
                m = AutoModelForCausalLM.from_pretrained(mp, attn_implementation="sdpa", device_map=dev, torch_dtype=dt, trust_remote_code=True).eval()
                p = AutoProcessor.from_pretrained(mp, trust_remote_code=True)
            except Exception:
                shutil.rmtree(mp)
                raise RuntimeError(f"Model load failed. Deleted {mp}. Please restart to re-download.")
        pmt = f"<{task}>"
        res = []
        for t in image:
            img = Image.fromarray((t.cpu().numpy() * 255).astype("uint8"))
            inputs = p(text=pmt, images=img, return_tensors="pt").to(dev, dt)
            with torch.no_grad():
                out = m.generate(input_ids=inputs["input_ids"], pixel_values=inputs["pixel_values"], max_new_tokens=max_tokens, num_beams=num_beams, do_sample=do_sample)
            txt = p.batch_decode(out, skip_special_tokens=False)[0]
            ans = p.post_process_generation(txt, task=pmt, image_size=img.size)
            res.append(ans[pmt] if pmt in ans else txt)
        return (", ".join(res),)
