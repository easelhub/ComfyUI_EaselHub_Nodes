import torch
import torch.nn.functional as F

class EHN_MaskProcessor:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "mask": ("MASK",),
                "invert": ("BOOLEAN", {"default": False}),
                "expansion": ("INT", {"default": 0, "min": -512, "max": 512, "step": 1}),
                "blur": ("INT", {"default": 0, "min": 0, "max": 256, "step": 1}),
            }
        }
    RETURN_TYPES = ("MASK",)
    FUNCTION = "execute"
    CATEGORY = "EaselHub Nodes/Mask"
    def execute(self, mask, invert, expansion, blur):
        m = mask.unsqueeze(1) if mask.dim() == 3 else mask
        if invert: m = 1.0 - m
        if expansion != 0:
            kernel = torch.ones(1, 1, 3, 3, device=m.device)
            pad = 1
            if expansion > 0:
                for _ in range(expansion): m = F.conv2d(m, kernel, padding=pad).clamp(0, 1)
            else:
                for _ in range(abs(expansion)): m = 1.0 - F.conv2d(1.0 - m, kernel, padding=pad).clamp(0, 1)
        if blur > 0:
            k = blur * 2 + 1
            sigma = blur / 3.0
            x = torch.arange(k, device=m.device).float() - k // 2
            g = torch.exp(-x**2 / (2 * sigma**2))
            g = g / g.sum()
            w = g.view(1, 1, 1, -1) * g.view(1, 1, -1, 1)
            m = F.conv2d(m, w, padding=k//2)
        return (m.squeeze(1),)