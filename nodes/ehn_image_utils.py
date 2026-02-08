import torch

class EHN_GetImageSize:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "side_choice": (["longest", "shortest"],),
            }
        }
    RETURN_TYPES = ("INT", "INT", "INT")
    RETURN_NAMES = ("side_length", "width", "height")
    FUNCTION = "execute"
    CATEGORY = "EaselHub Nodes/Utils"

    def execute(self, image, side_choice):
        _, H, W, _ = image.shape
        if side_choice == "longest":
            side = max(W, H)
        else:
            side = min(W, H)
        return (side, W, H)
