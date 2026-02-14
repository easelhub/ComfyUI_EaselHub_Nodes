import os, torch, random, string
from PIL import Image
from unittest.mock import patch
from transformers.dynamic_module_utils import get_imports
from transformers import AutoModelForCausalLM, AutoProcessor
import comfy.model_management as mm
import folder_paths

def fgi(f): return [x for x in get_imports(f) if x != "flash_attn"] if str(f).endswith("modeling_florence2.py") else get_imports(f)

class EHN_Florence2Tagger:
    CATEGORY, RETURN_TYPES, RETURN_NAMES, FUNCTION = "EaselHub/Tagger", ("STRING",), ("caption",), "tag"
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "model": (['Florence-2-large-PromptGen-v2.0', 'Florence-2-base-PromptGen-v2.0'], {"default": "Florence-2-large-PromptGen-v2.0"}),
            "image": ("IMAGE",),
            "method": (['tags', 'simple', 'detailed', 'extra', 'mixed', 'extra_mixed', 'analyze'], {"default": "extra_mixed"}),
            "max_tokens": ("INT", {"default": 1024, "min": 1, "max": 4096}),
            "random": (['never', 'always'], {"default": "never"})
        }}
    @classmethod
    def IS_CHANGED(s, **k): return "".join(random.choices(string.ascii_letters, k=8)) if k.get("random") == "always" else ""
    def tag(self, model, image, method, max_tokens, random):
        dev, dtype = mm.get_torch_device(), torch.float16
        mp = os.path.join(folder_paths.models_dir, "Florence-2", model)
        repo_model = model.replace("v2_0", "v2.0")
        if not os.path.exists(mp):
            from huggingface_hub import snapshot_download
            snapshot_download(repo_id=f"MiaoshouAI/{model}", local_dir=mp)
        with patch("transformers.dynamic_module_utils.get_imports", fgi):
            m = AutoModelForCausalLM.from_pretrained(mp, attn_implementation='sdpa', device_map=dev, torch_dtype=dtype, trust_remote_code=True).to(dev)
        p = AutoProcessor.from_pretrained(mp, trust_remote_code=True)
        imgs = [Image.fromarray(np.clip(255. * i.cpu().numpy(), 0, 255).astype(np.uint8)) for i in image]
        pmt = {"tags": "<GENERATE_TAGS>", "simple": "<CAPTION>", "detailed": "<DETAILED_CAPTION>", "extra": "<MORE_DETAILED_CAPTION>", "mixed": "<MIX_CAPTION>", "extra_mixed": "<MIX_CAPTION_PLUS>"}.get(method, "<ANALYZE>")
        res = []
        for i in imgs:
            inputs = p(text=pmt, images=i, return_tensors="pt").to(dtype).to(dev)
            out = m.generate(input_ids=inputs["input_ids"], pixel_values=inputs["pixel_values"], max_new_tokens=max_tokens, do_sample=random=='always', num_beams=3)
            res.append(p.post_process_generation(p.batch_decode(out, skip_special_tokens=False)[0], task=pmt, image_size=i.size)[pmt])
        return (", ".join(res),)
