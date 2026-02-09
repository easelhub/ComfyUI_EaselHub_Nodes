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
                "method": (["fit", "stretch", "cover", "letterbox"],),
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

    def execute(self, image, width, height, method, position, mask_expansion, mask_blur, mask_fill_holes, mask_invert, mask=None):
        B, H, W, C = image.shape
        if width == 0 and height == 0:
            target_mask = mask if mask is not None else torch.ones((B, H, W), device=image.device, dtype=image.dtype)
            return (image, process_mask_core(target_mask, mask_invert, mask_expansion, mask_blur, mask_fill_holes))
        
        target_w = width if width > 0 else max(1, round(W * height / H))
        target_h = height if height > 0 else max(1, round(H * width / W))
        resize_w, resize_h = target_w, target_h
        
        if method in ["fit", "cover", "letterbox"]:
            scale = min(target_w / W, target_h / H) if method != "cover" else max(target_w / W, target_h / H)
            resize_w, resize_h = max(1, round(W * scale)), max(1, round(H * scale))

        img_p = image.permute(0, 3, 1, 2)
        mask_p = mask.unsqueeze(1) if mask is not None else torch.ones((B, 1, H, W), device=image.device, dtype=image.dtype)
        if mask_p.shape[2:] != (H, W): mask_p = F.interpolate(mask_p, size=(H, W), mode="nearest")
        
        img_p = F.interpolate(img_p, size=(resize_h, resize_w), mode="bicubic", align_corners=False)
        mask_p = F.interpolate(mask_p, size=(resize_h, resize_w), mode="bilinear", align_corners=False)

        if method in ["cover", "letterbox"]:
            pad_h, pad_w = target_h - resize_h, target_w - resize_w
            if pad_h != 0 or pad_w != 0:
                def get_off(diff, pos, axis):
                    if pos == "center": return diff // 2
                    if axis == 'h': return 0 if "top" in pos else diff if "bottom" in pos else diff // 2
                    if axis == 'w': return 0 if "left" in pos else diff if "right" in pos else diff // 2
                    return diff // 2
                
                if method == "cover":
                    off_h, off_w = get_off(resize_h - target_h, position, 'h'), get_off(resize_w - target_w, position, 'w')
                    img_p = img_p[:, :, off_h:off_h+target_h, off_w:off_w+target_w]
                    mask_p = mask_p[:, :, off_h:off_h+target_h, off_w:off_w+target_w]
                else:
                    pt, pl = get_off(pad_h, position, 'h'), get_off(pad_w, position, 'w')
                    img_p = F.pad(img_p, (pl, pad_w - pl, pt, pad_h - pt), value=0)
                    mask_p = F.pad(mask_p, (pl, pad_w - pl, pt, pad_h - pt), value=0)

        return (img_p.permute(0, 2, 3, 1), process_mask_core(mask_p.squeeze(1), mask_invert, mask_expansion, mask_blur, mask_fill_holes))
