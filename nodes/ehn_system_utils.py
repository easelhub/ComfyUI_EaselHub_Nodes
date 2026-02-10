import torch
import gc

class EHN_SystemOptimizer:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {}, "optional": {"any_trigger": ("*",)}}
    RETURN_TYPES = ("*",)
    RETURN_NAMES = ("trigger",)
    FUNCTION = "execute"
    CATEGORY = "EaselHub Nodes/System"

    def execute(self, any_trigger=None):
        gc.collect()
        try:
            import comfy.model_management
            comfy.model_management.soft_empty_cache()
        except: pass
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()
        return (any_trigger,)