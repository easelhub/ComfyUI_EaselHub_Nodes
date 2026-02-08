import torch
import torch.nn.functional as F
from .ehn_mask_ops import process_mask_core

class EHN_ImageResize:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "width": ("INT", {"default": 512, "min": 0, "max": 8192, "step": 8}),
                "height": ("INT", {"default": 512, "min": 0, "max": 8192, "step": 8}),
                "method": (["stretch", "fit", "cover", "letterbox"],),
                "interpolation": (["nearest", "bilinear", "bicubic", "area"],),
                "position": (["center", "top", "bottom", "left", "right", "top-left", "top-right", "bottom-left", "bottom-right"],),
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

    def execute(self, image, width, height, method, interpolation, position, mask_expansion, mask_blur, mask_fill_holes, mask_invert, mask=None):
        B, H, W, C = image.shape
        if width == 0 and height == 0:
            target_mask = mask if mask is not None else torch.ones((B, H, W), device=image.device, dtype=image.dtype)
            target_mask = process_mask_core(target_mask, mask_invert, mask_expansion, mask_blur, mask_fill_holes)
            return (image, target_mask)
        target_w = width if width > 0 else max(1, round(W * height / H))
        target_h = height if height > 0 else max(1, round(H * width / W))
        resize_w, resize_h = target_w, target_h
        if method == "fit":
            scale = min(target_w / W, target_h / H)
            resize_w = max(1, round(W * scale))
            resize_h = max(1, round(H * scale))
        elif method == "cover" or method == "letterbox":
            scale = min(target_w / W, target_h / H) if method == "letterbox" else max(target_w / W, target_h / H)
            resize_w = max(1, round(W * scale))
            resize_h = max(1, round(H * scale))
        img_p = image.permute(0, 3, 1, 2)
        if mask is None:
            mask_p = torch.ones((B, 1, H, W), device=image.device, dtype=image.dtype)
        else:
            mask_p = mask.unsqueeze(1)
            if mask_p.shape[2:] != (H, W):
                mask_p = F.interpolate(mask_p, size=(H, W), mode="nearest")
        align = False if interpolation in ['bilinear', 'bicubic'] else None
        img_p = F.interpolate(img_p, size=(resize_h, resize_w), mode=interpolation, align_corners=align)
        mask_p = F.interpolate(mask_p, size=(resize_h, resize_w), mode="bilinear", align_corners=False)
        def get_off(diff, pos, axis):
            if pos == "center": return diff // 2
            if axis == 'h':
                if "top" in pos: return 0
                if "bottom" in pos: return diff
            if axis == 'w':
                if "left" in pos: return 0
                if "right" in pos: return diff
            return diff // 2
        if method == "cover":
            if resize_h > target_h:
                diff = resize_h - target_h
                off = get_off(diff, position, 'h')
                img_p = img_p[:, :, off:off+target_h, :]
                mask_p = mask_p[:, :, off:off+target_h, :]
            if resize_w > target_w:
                diff = resize_w - target_w
                off = get_off(diff, position, 'w')
                img_p = img_p[:, :, :, off:off+target_w]
                mask_p = mask_p[:, :, :, off:off+target_w]
        elif method == "letterbox":
            ph = target_h - resize_h
            pw = target_w - resize_w
            if ph > 0 or pw > 0:
                pt = get_off(ph, position, 'h')
                pb = ph - pt
                pl = get_off(pw, position, 'w')
                pr = pw - pl
                img_p = F.pad(img_p, (pl, pr, pt, pb), value=0)
                mask_p = F.pad(mask_p, (pl, pr, pt, pb), value=0)
        mask_out = mask_p.squeeze(1)
        mask_out = process_mask_core(mask_out, mask_invert, mask_expansion, mask_blur, mask_fill_holes)
        return (img_p.permute(0, 2, 3, 1), mask_out)
