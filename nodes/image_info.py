import torch

class EHN_GetImageSize:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "side_choice": (["Longest", "Shortest"], {"default": "Longest"}),
            }
        }
    RETURN_TYPES = ("INT", "INT", "INT")
    RETURN_NAMES = ("selected", "width", "height")
    FUNCTION = "execute"
    CATEGORY = "EaselHub/Image"

    def execute(self, image, side_choice):
        _, H, W, _ = image.shape
        s = max(H, W) if side_choice == "Longest" else min(H, W)
        return (s, W, H)
