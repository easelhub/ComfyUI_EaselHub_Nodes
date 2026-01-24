import torch
import gc
import comfy.model_management

# --- Universal Type ---
class AnyType(str):
    """A wildcard type for ComfyUI nodes to accept any input."""
    def __ne__(self, __value: object) -> bool:
        return False
    def __eq__(self, __value: object) -> bool:
        return True

any_type = AnyType("*")

# --- Utils Nodes ---
class EHN_ImageSideCalc:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "side": (["Longest", "Shortest", "Width", "Height"], {"default": "Longest"}),
            }
        }

    RETURN_TYPES = ("INT",)
    RETURN_NAMES = ("value",)
    FUNCTION = "get_side"
    CATEGORY = "EaselHub/Utils"

    def get_side(self, image, side):
        _, h, w, _ = image.shape
        if side == "Width": val = w
        elif side == "Height": val = h
        elif side == "Longest": val = max(h, w)
        else: val = min(h, w)
        return (val,)

class EHN_FreeVRAM:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "mode": (["Soft (Empty Cache)", "Hard (Unload Models)"], {"default": "Soft (Empty Cache)"}),
            },
            "optional": { "any_input": (any_type,), }
        }

    RETURN_TYPES = (any_type,)
    RETURN_NAMES = ("passthrough",)
    FUNCTION = "clear_vram"
    CATEGORY = "EaselHub/Utils"
    OUTPUT_NODE = True

    def clear_vram(self, mode, any_input=None):
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()
        if mode == "Hard (Unload Models)":
            comfy.model_management.unload_all_models()
        comfy.model_management.soft_empty_cache()
        return (any_input,)