import torch
import gc
import sys

class EHN_SystemOptimizer:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "mode": (["Soft Release", "Hard Release", "VRAM Defrag"],),
            },
            "optional": {
                "any_trigger": ("*",),
            }
        }
    RETURN_TYPES = ("*",)
    RETURN_NAMES = ("trigger",)
    FUNCTION = "execute"
    CATEGORY = "EaselHub Nodes/System"
    def execute(self, mode, any_trigger=None):
        gc.collect()
        try:
            import comfy.model_management
            mm = comfy.model_management
            if mode == "Soft Release":
                mm.soft_empty_cache()
            elif mode == "Hard Release":
                mm.cleanup_models()
                mm.soft_empty_cache()
        except: pass
        if torch.cuda.is_available():
            if mode == "VRAM Defrag":
                torch.cuda.empty_cache()
                torch.cuda.ipc_collect()
            else:
                torch.cuda.empty_cache()
        return (any_trigger,)