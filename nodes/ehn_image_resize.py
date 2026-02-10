import torch
import torch.nn.functional as F
from .ehn_mask_ops import process_mask_core

class EHN_ImageResize:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "width": ("INT", {"default": 1024, "min": 0, "max": 8192, "step": 8}),
                "height": ("INT", {"default": 1024, "min": 0, "max": 8192, "step": 8}),
                "interpolation": (["nearest", "bilinear", "bicubic", "area"], {"default": "bicubic"}),
                "method": (["stretch", "keep proportion", "fill / crop", "pad"], {"default": "keep proportion"}),
                "condition": (["always", "downscale if bigger", "upscale if smaller", "if bigger area", "if smaller area"], {"default": "always"}),
                "multiple_of": ("INT", {"default": 8, "min": 0, "max": 512, "step": 8}),
                "mask_expansion": ("INT", {"default": 0, "min": -128, "max": 128, "step": 1}),
                "mask_blur": ("INT", {"default": 0, "min": 0, "max": 64, "step": 1}),
                "mask_fill_holes": ("BOOLEAN", {"default": False}),
                "mask_invert": ("BOOLEAN", {"default": False}),
            },
            "optional": {
                "mask": ("MASK",),
            }
        }
    RETURN_TYPES = ("IMAGE", "MASK")
    RETURN_NAMES = ("image", "mask")
    FUNCTION = "execute"
    CATEGORY = "EaselHub Nodes/Image"

    def execute(self, image, width, height, interpolation, method, condition, multiple_of, mask_expansion, mask_blur, mask_fill_holes, mask_invert, mask=None):
        B, H, W, C = image.shape
        
        if width == 0 and height == 0:
            target_mask = mask if mask is not None else torch.ones((B, H, W), device=image.device, dtype=image.dtype)
            return (image, process_mask_core(target_mask, mask_invert, mask_expansion, mask_blur, mask_fill_holes))

        target_width = width
        target_height = height

        if width == 0:
            target_width = max(1, round(W * height / H))
        elif height == 0:
            target_height = max(1, round(H * width / W))

        if multiple_of > 1:
            target_width = target_width - (target_width % multiple_of)
            target_height = target_height - (target_height % multiple_of)

        if condition == "downscale if bigger":
            if method == "fill / crop":
                if W <= target_width and H <= target_height:
                    target_width, target_height = W, H
            elif W <= target_width or H <= target_height:
                target_width, target_height = W, H
        elif condition == "upscale if smaller":
            if method == "fill / crop":
                if W >= target_width and H >= target_height:
                    target_width, target_height = W, H
            elif W >= target_width or H >= target_height:
                target_width, target_height = W, H
        elif condition == "if bigger area":
            if W * H <= target_width * target_height:
                target_width, target_height = W, H
        elif condition == "if smaller area":
            if W * H >= target_width * target_height:
                target_width, target_height = W, H

        if method == "keep proportion" or method == "pad":
            scale = min(target_width / W, target_height / H)
            resize_width = max(1, round(W * scale))
            resize_height = max(1, round(H * scale))
        elif method == "fill / crop":
            scale = max(target_width / W, target_height / H)
            resize_width = max(1, round(W * scale))
            resize_height = max(1, round(H * scale))
        else:
            resize_width = target_width
            resize_height = target_height

        if resize_width != W or resize_height != H:
            image = image.permute(0, 3, 1, 2)
            image = F.interpolate(image, size=(resize_height, resize_width), mode=interpolation)
            image = image.permute(0, 2, 3, 1)
            if mask is not None:
                mask = F.interpolate(mask.unsqueeze(1), size=(resize_height, resize_width), mode="nearest").squeeze(1)

        if method == "pad":
            pad_w = target_width - resize_width
            pad_h = target_height - resize_height
            pad_l = pad_w // 2
            pad_t = pad_h // 2
            
            if pad_w > 0 or pad_h > 0:
                image = image.permute(0, 3, 1, 2)
                image = F.pad(image, (pad_l, pad_w - pad_l, pad_t, pad_h - pad_t), value=0)
                image = image.permute(0, 2, 3, 1)
                if mask is not None:
                    mask = F.pad(mask, (pad_l, pad_w - pad_l, pad_t, pad_h - pad_t), value=0)
                else:
                    mask = torch.zeros((B, target_height, target_width), device=image.device, dtype=image.dtype)
                    mask[:, pad_t:target_height-(pad_h-pad_t), pad_l:target_width-(pad_w-pad_l)] = 1.0

        elif method == "fill / crop":
            crop_w = resize_width - target_width
            crop_h = resize_height - target_height
            crop_l = crop_w // 2
            crop_t = crop_h // 2
            
            if crop_w > 0 or crop_h > 0:
                image = image[:, crop_t:crop_t+target_height, crop_l:crop_l+target_width, :]
                if mask is not None:
                    mask = mask[:, crop_t:crop_t+target_height, crop_l:crop_l+target_width]

        if mask is None:
            mask = torch.ones((B, target_height, target_width), device=image.device, dtype=image.dtype)

        return (image, process_mask_core(mask, mask_invert, mask_expansion, mask_blur, mask_fill_holes))