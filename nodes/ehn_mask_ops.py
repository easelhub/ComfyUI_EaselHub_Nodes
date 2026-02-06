import torch
import torch.nn.functional as F
import numpy as np
import scipy.ndimage

def process_mask_core(mask, invert, expansion, blur, fill_holes):
    device = mask.device
    if fill_holes:
        m = mask.cpu().numpy()
        for i in range(m.shape[0]):
            m_bool = m[i] > 0.5
            m[i] = scipy.ndimage.binary_fill_holes(m_bool).astype(np.float32)
        mask = torch.from_numpy(m).to(device)
    
    m_tensor = mask.unsqueeze(1)
    
    if expansion != 0:
        val = abs(expansion)
        kernel_size = val * 2 + 1
        if expansion > 0:
            m_tensor = F.max_pool2d(m_tensor, kernel_size=kernel_size, stride=1, padding=val)
        else:
            m_tensor = 1.0 - m_tensor
            m_tensor = F.max_pool2d(m_tensor, kernel_size=kernel_size, stride=1, padding=val)
            m_tensor = 1.0 - m_tensor

    if blur > 0:
        k_size = blur * 4 + 1
        x = torch.arange(k_size, device=device) - k_size // 2
        x = x.float()
        gx = torch.exp(-x**2 / (2 * blur**2))
        gx = gx / gx.sum()
        weights = (gx[:, None] * gx[None, :]).unsqueeze(0).unsqueeze(0)
        m_tensor = F.conv2d(m_tensor, weights, padding=k_size//2)

    m_tensor = m_tensor.squeeze(1)
    
    if invert:
        m_tensor = 1.0 - m_tensor
        
    return torch.clamp(m_tensor, 0.0, 1.0)

class EHN_MaskProcessor:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "mask": ("MASK",),
                "invert": ("BOOLEAN", {"default": False}),
                "expansion": ("INT", {"default": 0, "min": -128, "max": 128, "step": 1}),
                "blur": ("INT", {"default": 0, "min": 0, "max": 64, "step": 1}),
                "fill_holes": ("BOOLEAN", {"default": False}),
            }
        }
    RETURN_TYPES = ("MASK",)
    RETURN_NAMES = ("mask",)
    FUNCTION = "execute"
    CATEGORY = "EaselHub Nodes/Mask"

    def execute(self, mask, invert, expansion, blur, fill_holes):
        return (process_mask_core(mask, invert, expansion, blur, fill_holes),)
