import torch
import torch.nn.functional as F
import numpy as np
import cv2

class EHN_MaskProcess:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "mask": ("MASK",),
                "blur": ("INT", {"default": 0, "min": 0, "max": 512, "step": 1}),
                "grow": ("INT", {"default": 0, "min": -512, "max": 512, "step": 1}),
                "invert": ("BOOLEAN", {"default": False}),
                "fill_holes": ("BOOLEAN", {"default": False}),
            }
        }
    RETURN_TYPES = ("MASK",)
    RETURN_NAMES = ("mask",)
    FUNCTION = "execute"
    CATEGORY = "EaselHub/Mask"

    def execute(self, mask, blur, grow, invert, fill_holes):
        if len(mask.shape) == 2: mask = mask.unsqueeze(0)
        if fill_holes:
            mask_np = mask.cpu().numpy()
            for i in range(mask_np.shape[0]):
                m = (mask_np[i] * 255).astype(np.uint8)
                contours, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                cv2.drawContours(m, contours, -1, 255, -1)
                mask_np[i] = m.astype(np.float32) / 255.0
            mask = torch.from_numpy(mask_np).to(mask.device)
        if grow != 0:
            m = mask.unsqueeze(1)
            k = abs(grow) * 2 + 1
            p = abs(grow)
            m = F.max_pool2d(m if grow > 0 else -m, k, stride=1, padding=p)
            mask = (m if grow > 0 else -m).squeeze(1)
        if blur > 0:
            k_sz = blur * 2 + 1
            sigma = blur / 3.0
            x = torch.arange(k_sz, device=mask.device).float() - blur
            k = torch.exp(-0.5 * (x / sigma) ** 2)
            k = (k / k.sum()).view(1, 1, -1, 1)
            m = F.pad(mask.unsqueeze(1), (blur, blur, blur, blur), mode='replicate')
            mask = F.conv2d(F.conv2d(m, k, groups=1), k.transpose(2, 3), groups=1).squeeze(1)
        if invert: mask = 1.0 - mask
        return (mask,)
