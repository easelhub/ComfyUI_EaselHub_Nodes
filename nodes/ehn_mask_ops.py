import torch, torch.nn.functional as F, numpy as np

class EHN_MaskFillHoles:
    @classmethod
    def INPUT_TYPES(s): return {"required": {"mask": ("MASK",),"mask_blur": ("INT", {"default": 0}),  "fill_holes": ("BOOLEAN", {"default": True}), "invert_mask": ("BOOLEAN", {"default": False})}}
    RETURN_TYPES = ("MASK",); FUNCTION = "fill"; CATEGORY = "EaselHub/Mask"
    DESCRIPTION = "Fills holes in masks, blurs edges, or inverts the mask."
    def fill(self, mask, fill_holes, mask_blur, invert_mask):
        try: from scipy.ndimage import binary_fill_holes
        except: return (mask,)
        out = []
        for m in mask.cpu().numpy():
            f = m
            if fill_holes:
                f = binary_fill_holes(m > 0.5).astype(np.float32)
            f = torch.from_numpy(f).to(mask.device)
            if mask_blur > 0: f = F.avg_pool2d(F.pad(f[None,None], [mask_blur]*4, mode='reflect'), mask_blur*2+1, 1)[0,0]
            out.append(1.0 - f if invert_mask else f)
        return (torch.stack(out),)