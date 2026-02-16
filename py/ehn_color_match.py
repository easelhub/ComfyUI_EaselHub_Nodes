import torch, numpy as np
from color_matcher import ColorMatcher

class EHN_ColorMatch:
    CATEGORY, RETURN_TYPES, RETURN_NAMES, FUNCTION = "EaselHub/Image", ("IMAGE",), ("image",), "match"
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "ref_image": ("IMAGE",),
            "target_image": ("IMAGE",),
            "method": (["mkl", "hm", "reinhard", "mvgd", "hm-mvgd-hm", "hm-mkl-hm"], {"default": "mkl"}),
        }}

    def match(self, ref_image, target_image, method):
        cm = ColorMatcher()
        t_imgs = target_image.cpu().numpy() if target_image.ndim == 4 else target_image.unsqueeze(0).cpu().numpy()
        r_imgs = ref_image.cpu().numpy() if ref_image.ndim == 4 else ref_image.unsqueeze(0).cpu().numpy()
        
        res = []
        for i in range(len(t_imgs)):
            r_img = r_imgs[i % len(r_imgs)]
            matched = cm.transfer(src=t_imgs[i], ref=r_img, method=method)
            res.append(torch.from_numpy(matched))
            
        return (torch.stack(res),)
