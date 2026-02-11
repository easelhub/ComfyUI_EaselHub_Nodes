import torch

class EHN_GetImageSize:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "mode": (["longest", "shortest"],),
            }
        }
    RETURN_TYPES = ("INT", "INT", "INT")
    RETURN_NAMES = ("value", "width", "height")
    FUNCTION = "execute"
    CATEGORY = "EaselHub Nodes/Utils"
    def execute(self, image, mode):
        _, H, W, _ = image.shape
        val = max(W, H) if mode == "longest" else min(W, H)
        return (val, W, H)