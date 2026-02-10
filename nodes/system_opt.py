import torch
import gc
import comfy.model_management

class EHN_SystemOptimizer:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "any_input": ("*",),
                "mode": (["VRAM + RAM", "VRAM Only", "RAM Only"], {"default": "VRAM + RAM"}),
            }
        }
    RETURN_TYPES = ("*",)
    RETURN_NAMES = ("output",)
    FUNCTION = "execute"
    CATEGORY = "EaselHub/System"

    def execute(self, any_input, mode):
        if "RAM" in mode: gc.collect()
        if "VRAM" in mode:
            comfy.model_management.soft_empty_cache()
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()
        return (any_input,)
