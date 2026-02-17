import torch, numpy as np
from color_matcher import ColorMatcher

class EHN_ColorMatch:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "reference_image": ("IMAGE",),
                "source_image": ("IMAGE",),
                "method": (["hm-mkl-hm", "hm-mvgd-hm", "mkl", "hm", "reinhard", "mvgd"], {"default": "hm-mkl-hm"}),
            }
        }
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "execute"
    CATEGORY = "EaselHub/Image"

    def execute(self, reference_image, source_image, method):
        cm = ColorMatcher()
        src = source_image.cpu().numpy()
        ref = reference_image.cpu().numpy()
        B = src.shape[0]
        R = ref.shape[0]
        res = []
        for i in range(B):
            r_img = ref[i % R]
            matched = cm.transfer(src=src[i], ref=r_img, method=method)
            res.append(torch.from_numpy(matched))
        return (torch.stack(res),)
