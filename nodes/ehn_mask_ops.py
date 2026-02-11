import torch
import torch.nn.functional as F
import numpy as np

def process_mask_core(mask, invert, expansion, blur, fill_holes):
    m = mask.unsqueeze(1) if mask.dim() == 3 else mask
    
    if fill_holes:
        try:
            from scipy.ndimage import binary_fill_holes
            device = m.device
            m_np = m.cpu().numpy()
            out_np = np.zeros_like(m_np)
            for i in range(m_np.shape[0]):
                out_np[i, 0] = binary_fill_holes(m_np[i, 0] > 0.5).astype(np.float32)
            m = torch.from_numpy(out_np).to(device)
        except: pass

    if expansion != 0:
        kernel = torch.ones(1, 1, 3, 3, device=m.device)
        if expansion > 0:
            for _ in range(expansion): m = F.conv2d(m, kernel, padding=1).clamp(0, 1)
        else:
            for _ in range(abs(expansion)): m = 1.0 - F.conv2d(1.0 - m, kernel, padding=1).clamp(0, 1)

    if invert: m = 1.0 - m
            
    if blur > 0:
        k = blur * 2 + 1
        sigma = blur / 3.0
        x = torch.arange(k, device=m.device).float() - k // 2
        g = torch.exp(-x**2 / (2 * sigma**2))
        g = g / g.sum()
        w = g.view(1, 1, 1, -1) * g.view(1, 1, -1, 1)
        m = F.conv2d(m, w, padding=k//2)
        
    return m.squeeze(1)

class EHN_MaskProcessor:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "mask": ("MASK",),
                "invert": ("BOOLEAN", {"default": False}),
                "expansion": ("INT", {"default": 0, "min": -512, "max": 512, "step": 1}),
                "blur": ("INT", {"default": 0, "min": 0, "max": 256, "step": 1}),
                "fill_holes": ("BOOLEAN", {"default": False}),
            }
        }
    RETURN_TYPES = ("MASK",)
    FUNCTION = "execute"
    CATEGORY = "EaselHub Nodes/Mask"
    def execute(self, mask, invert, expansion, blur, fill_holes):
        return (process_mask_core(mask, invert, expansion, blur, fill_holes),)