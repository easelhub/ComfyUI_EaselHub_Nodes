import random, time
class Easel_Seed:
    NAME, CATEGORY = "Easel_Seed", "EaselHub/Utils"
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {"seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff})}, "hidden": {"prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO", "unique_id": "UNIQUE_ID"}}
    RETURN_TYPES, RETURN_NAMES, FUNCTION = ("INT",), ("SEED",), "main"
    @classmethod
    def IS_CHANGED(s, seed, **kwargs):
        return float("nan") if seed < 0 else seed
    def main(self, seed=0, prompt=None, extra_pnginfo=None, unique_id=None):
        if seed < 0:
            seed = int(time.time() * 1000) % 0xffffffffffffffff
            if unique_id and prompt and str(unique_id) in prompt: prompt[str(unique_id)]['inputs']['seed'] = seed
            if unique_id and extra_pnginfo and 'workflow' in extra_pnginfo:
                node = next((x for x in extra_pnginfo['workflow']['nodes'] if str(x['id']) == str(unique_id)), None)
                if node: node['widgets_values'] = [seed]
        return (seed,)
