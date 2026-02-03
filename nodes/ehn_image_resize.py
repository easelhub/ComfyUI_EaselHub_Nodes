import torch, torch.nn.functional as F, math
import comfy.utils
from .ehn_utils import fill_mask_holes

class EHN_ImageResize:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "width": ("INT", {"default": 0, "max": 16384}),
                "height": ("INT", {"default": 0, "max": 16384}),
                "interpolation": (["nearest", "bilinear", "bicubic", "area", "lanczos"], {"default": "bicubic"}),
                "method": (["stretch", "keep proportion", "fill / crop", "pad (letterbox)", "scale to Target MP (Maintain Ratio)"], {"default": "stretch"}),
                "crop_pad_pos": (["center", "top", "bottom", "left", "right", "top-left", "top-right", "bottom-left", "bottom-right"], {"default": "center"}),
                "condition": (["always", "downscale only", "upscale only"], {"default": "always"}),
                "multiple_of": ("INT", {"default": 32, "max": 512}),
                "target_mp": ("FLOAT", {"default": 1.0, "step": 0.1}),
                "mask_blur": ("INT", {"default": 0}),
                "fill_holes": ("BOOLEAN", {"default": False}),
            },
            "optional": { "mask": ("MASK",) }
        }
    RETURN_TYPES = ("IMAGE", "MASK", "INT", "INT")
    RETURN_NAMES = ("image", "mask", "width", "height")
    FUNCTION = "execute"
    CATEGORY = "EaselHub/Image"

    def execute(self, image, width, height, target_mp, interpolation, method, condition, multiple_of, fill_holes, mask_blur, crop_pad_pos="center", mask=None):
        b, h, w, c = image.shape
        tw, th = width, height

        if method == "scale to Target MP (Maintain Ratio)":
            s = math.sqrt((target_mp * 1e6) / (w * h + 1e-6))
            tw, th = int(w * s), int(h * s)
        elif width == 0 and height == 0: tw, th = w, h
        elif width == 0: tw = int(w * (height / h))
        elif height == 0: th = int(h * (width / w))

        rw, rh = tw, th
        if method not in ["stretch", "scale to Target MP (Maintain Ratio)"]:
            sw, sh = tw / w, th / h
            s = min(sw, sh) if method in ["keep proportion", "pad (letterbox)"] else max(sw, sh)
            rw, rh = int(w * s), int(h * s)

        if multiple_of > 1:
            rw, rh = max(multiple_of, (rw // multiple_of) * multiple_of), max(multiple_of, (rh // multiple_of) * multiple_of)
            if method == "stretch": tw, th = rw, rh

        if (condition == "downscale only" and rw >= w and rh >= h) or (condition == "upscale only" and rw <= w and rh <= h):
            if mask is None: mask = torch.zeros((b, h, w), device=image.device)
            elif mask.dim() == 2: mask = mask.unsqueeze(0).repeat(b, 1, 1)
            return (image, mask, w, h)

        if mask is None: mask = torch.zeros((b, h, w), device=image.device)
        elif mask.dim() == 2: mask = mask.unsqueeze(0).repeat(b, 1, 1)

        if interpolation == "lanczos":
            # common_upscale returns BHWC, we need BCHW for subsequent operations
            img_res = comfy.utils.common_upscale(image.movedim(-1,1), rw, rh, "lanczos", "disabled").movedim(1,-1).permute(0, 3, 1, 2)
        else:
            img_res = F.interpolate(image.permute(0, 3, 1, 2), size=(rh, rw), mode=interpolation)
        
        mask_res = F.interpolate(mask.unsqueeze(1), size=(rh, rw), mode="nearest" if interpolation=="nearest" else "bilinear")

        if method == "fill / crop" or method == "pad (letterbox)":
            if method == "fill / crop":
                dx, dy = max(0, rw - tw), max(0, rh - th)
                x, y = dx // 2, dy // 2
                if "left" in crop_pad_pos: x = 0
                elif "right" in crop_pad_pos: x = dx
                if "top" in crop_pad_pos: y = 0
                elif "bottom" in crop_pad_pos: y = dy
                img_res = img_res[..., y:y+th, x:x+tw]
                mask_res = mask_res[..., y:y+th, x:x+tw]
            else:
                pw, ph = max(0, tw - rw), max(0, th - rh)
                pl, pt = pw // 2, ph // 2
                if "left" in crop_pad_pos: pl = 0
                elif "right" in crop_pad_pos: pl = pw
                if "top" in crop_pad_pos: pt = 0
                elif "bottom" in crop_pad_pos: pt = ph
                pad = (pl, pw - pl, pt, ph - pt)
                img_res = F.pad(img_res, pad)
                mask_res = F.pad(mask_res, pad)

        if fill_holes:
            mask_res = fill_mask_holes(mask_res)

        if mask_blur > 0:
            mask_res = F.avg_pool2d(F.pad(mask_res.unsqueeze(1), [mask_blur]*4, mode='reflect'), mask_blur*2+1, 1).squeeze(1)

        return (img_res.permute(0, 2, 3, 1), mask_res.squeeze(1), img_res.shape[3], img_res.shape[2])