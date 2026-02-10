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

        if resize_mode == "width":
            new_w = width
            new_h = int(H * (width / W))
        elif resize_mode == "height":
            new_w = int(W * (height / H))
            new_h = height
        elif resize_mode == "stretch":
            new_w = width
            new_h = height
        elif resize_mode == "fit":
            scale = min(width / W, height / H)
            new_w = int(W * scale)
            new_h = int(H * scale)
        elif resize_mode == "fill":
            scale = max(width / W, height / H)
            new_w = int(W * scale)
            new_h = int(H * scale)
        else:
            new_w, new_h = width, height

        new_w = max(divisible_by, (new_w // divisible_by) * divisible_by)
        new_h = max(divisible_by, (new_h // divisible_by) * divisible_by)

        image = image.permute(0, 3, 1, 2)
        align_corners = False if method not in ["nearest", "area"] else None
        image = F.interpolate(image, size=(new_h, new_w), mode=method, align_corners=align_corners)
        image = image.permute(0, 2, 3, 1)

        if mask is not None:
            if len(mask.shape) == 2: mask = mask.unsqueeze(0)
            mask = mask.unsqueeze(1)
            mask = F.interpolate(mask, size=(new_h, new_w), mode="nearest")
            mask = mask.squeeze(1)
        else:
            mask = torch.zeros((B, new_h, new_w), device=image.device)

        if crop != "none" and resize_mode == "fill":
            crop_w = min(new_w, width)
            crop_h = min(new_h, height)
            
            if crop_w < new_w or crop_h < new_h:
                dx = (new_w - crop_w) // 2
                dy = (new_h - crop_h) // 2
                
                if crop == "top": dy = 0
                elif crop == "bottom": dy = new_h - crop_h
                elif crop == "left": dx = 0
                elif crop == "right": dx = new_w - crop_w
                
                image = image[:, dy:dy+crop_h, dx:dx+crop_w, :]
                mask = mask[:, dy:dy+crop_h, dx:dx+crop_w]

        if mask_fill_holes:
            mask_np = mask.cpu().numpy()
            for i in range(mask_np.shape[0]):
                m = (mask_np[i] * 255).astype(np.uint8)
                contours, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                filled = np.zeros_like(m)
                cv2.drawContours(filled, contours, -1, 255, -1)
                mask_np[i] = filled.astype(np.float32) / 255.0
            mask = torch.from_numpy(mask_np).to(mask.device)

        if mask_grow != 0:
            m = mask.unsqueeze(1)
            kernel_size = abs(mask_grow) * 2 + 1
            padding = abs(mask_grow)
            if mask_grow > 0:
                m = F.max_pool2d(m, kernel_size, stride=1, padding=padding)
            else:
                m = -F.max_pool2d(-m, kernel_size, stride=1, padding=padding)
            mask = m.squeeze(1)

        if mask_blur > 0:
            kernel_size = mask_blur * 2 + 1
            sigma = mask_blur / 3.0
            x = torch.arange(kernel_size, device=mask.device).float() - mask_blur
            k = torch.exp(-0.5 * (x / sigma) ** 2)
            k = k / k.sum()
            k = k.view(1, 1, -1, 1)
            ky = k.transpose(2, 3)
            m = mask.unsqueeze(1)
            m = F.pad(m, (mask_blur, mask_blur, mask_blur, mask_blur), mode='replicate')
            m = F.conv2d(m, k, groups=1)
            m = F.conv2d(m, ky, groups=1)
            mask = m.squeeze(1)

        if mask_invert:
            mask = 1.0 - mask

        return (image, mask)
