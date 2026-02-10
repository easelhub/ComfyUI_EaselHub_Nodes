import torch
import torch.nn.functional as F
import numpy as np
import cv2

class EHN_ImageResize:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "width": ("INT", {"default": 1024, "min": 0, "max": 8192, "step": 8}),
                "height": ("INT", {"default": 1024, "min": 0, "max": 8192, "step": 8}),
                "resize_mode": (["stretch", "fit", "fill", "width", "height"], {"default": "fit"}),
                "method": (["nearest", "bilinear", "bicubic", "area"], {"default": "bicubic"}),
                "crop": (["center", "top", "bottom", "left", "right", "none"], {"default": "center"}),
                "divisible_by": ("INT", {"default": 8, "min": 1, "max": 128, "step": 1}),
            },
            "optional": {
                "mask": ("MASK",),
                "mask_blur": ("INT", {"default": 0, "min": 0, "max": 512, "step": 1}),
                "mask_invert": ("BOOLEAN", {"default": False}),
                "mask_grow": ("INT", {"default": 0, "min": -512, "max": 512, "step": 1}),
                "mask_fill_holes": ("BOOLEAN", {"default": False}),
            }
        }
    RETURN_TYPES = ("IMAGE", "MASK")
    RETURN_NAMES = ("image", "mask")
    FUNCTION = "execute"
    CATEGORY = "EaselHub/Image"

    def execute(self, image, width, height, resize_mode, method, crop, divisible_by, mask=None, mask_blur=0, mask_invert=False, mask_grow=0, mask_fill_holes=False):
        B, H, W, C = image.shape
        if width == 0: width = W
        if height == 0: height = H
        if resize_mode == "width": new_w, new_h = width, int(H * (width / W))
        elif resize_mode == "height": new_w, new_h = int(W * (height / H)), height
        elif resize_mode == "stretch": new_w, new_h = width, height
        elif resize_mode == "fit":
            s = min(width / W, height / H)
            new_w, new_h = int(W * s), int(H * s)
        elif resize_mode == "fill":
            s = max(width / W, height / H)
            new_w, new_h = int(W * s), int(H * s)
        else: new_w, new_h = width, height
        new_w = max(divisible_by, (new_w // divisible_by) * divisible_by)
        new_h = max(divisible_by, (new_h // divisible_by) * divisible_by)
        
        img = image.permute(0, 3, 1, 2)
        img = F.interpolate(img, size=(new_h, new_w), mode=method, align_corners=False if method not in ["nearest", "area"] else None)
        img = img.permute(0, 2, 3, 1)

        if mask is None: mask = torch.zeros((B, new_h, new_w), device=image.device, dtype=torch.float32)
        else:
            if len(mask.shape) == 2: mask = mask.unsqueeze(0)
            mask = F.interpolate(mask.unsqueeze(1), size=(new_h, new_w), mode="nearest").squeeze(1)

        if crop != "none" and resize_mode == "fill":
            cw, ch = min(new_w, width), min(new_h, height)
            if cw < new_w or ch < new_h:
                dx, dy = (new_w - cw) // 2, (new_h - ch) // 2
                if crop == "top": dy = 0
                elif crop == "bottom": dy = new_h - ch
                elif crop == "left": dx = 0
                elif crop == "right": dx = new_w - cw
                img = img[:, dy:dy+ch, dx:dx+cw, :]
                mask = mask[:, dy:dy+ch, dx:dx+cw]

        if mask_fill_holes:
            mnp = mask.cpu().numpy()
            for i in range(mnp.shape[0]):
                m = (mnp[i] * 255).astype(np.uint8)
                cts, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                cv2.drawContours(m, cts, -1, 255, -1)
                mnp[i] = m.astype(np.float32) / 255.0
            mask = torch.from_numpy(mnp).to(mask.device)

        if mask_grow != 0:
            k = abs(mask_grow) * 2 + 1
            p = abs(mask_grow)
            m = mask.unsqueeze(1)
            m = F.max_pool2d(m if mask_grow > 0 else -m, k, stride=1, padding=p)
            mask = (m if mask_grow > 0 else -m).squeeze(1)

        if mask_blur > 0:
            k = mask_blur * 2 + 1
            s = mask_blur / 3.0
            x = torch.arange(k, device=mask.device).float() - mask_blur
            k_t = torch.exp(-0.5 * (x / s) ** 2)
            k_t = (k_t / k_t.sum()).view(1, 1, -1, 1)
            m = F.pad(mask.unsqueeze(1), (mask_blur, mask_blur, mask_blur, mask_blur), mode='replicate')
            mask = F.conv2d(F.conv2d(m, k_t, groups=1), k_t.transpose(2, 3), groups=1).squeeze(1)

        if mask_invert: mask = 1.0 - mask
        
        return (img, mask)
