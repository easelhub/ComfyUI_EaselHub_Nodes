import torch
import torch.nn.functional as F
import math

class EHN_ImageResize:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "width": ("INT", {"default": 0, "max": 16384}),
                "height": ("INT", {"default": 0, "max": 16384}),
                "interpolation": (["nearest", "bilinear", "bicubic", "area", "lanczos"], {"default": "bicubic"}),
                "method": (["Stretch", "Keep Proportion", "Fill / Crop", "Pad (Letterbox)", "Scale to Target MP"], {"default": "Stretch"}),
                "crop_pad_pos": (["center", "top", "bottom", "left", "right", "top-left", "top-right", "bottom-left", "bottom-right"], {"default": "center"}),
                "condition": (["Always", "Downscale Only", "Upscale Only"], {"default": "Always"}),
                "multiple_of": ("INT", {"default": 32, "max": 512}),
                "target_mp": ("FLOAT", {"default": 1.0, "step": 0.1}),
                "mask_blur": ("INT", {"default": 0}),
                "fill_holes": ("BOOLEAN", {"default": False}),
            },
            "optional": {"mask": ("MASK",)}
        }
    RETURN_TYPES = ("IMAGE", "MASK", "INT", "INT")
    RETURN_NAMES = ("image", "mask", "width", "height")
    FUNCTION = "execute"
    CATEGORY = "EaselHub/Image"
    
    def execute(self, image, width, height, target_mp, interpolation, method, condition, multiple_of, fill_holes, mask_blur, crop_pad_pos="center", mask=None):
        b, h, w, c = image.shape
        tw, th = width, height
        method = method.lower()
        if "scale to target mp" in method: method = "scale_mp"
        elif "pad" in method: method = "pad"
        elif "fill" in method: method = "fill"
        elif "proportion" in method: method = "proportion"
        else: method = "stretch"
        condition = condition.lower()
        
        if method == "scale_mp":
            s = math.sqrt((target_mp * 1e6) / (w * h + 1e-6))
            tw, th = int(w * s), int(h * s)
        elif width == 0 and height == 0: tw, th = w, h
        elif width == 0: tw = int(w * (height / h))
        elif height == 0: th = int(h * (width / w))

        if condition == "downscale only" and (tw >= w and th >= h): return (image, mask if mask is not None else torch.zeros((b,h,w)), w, h)
        if condition == "upscale only" and (tw <= w and th <= h): return (image, mask if mask is not None else torch.zeros((b,h,w)), w, h)

        tw = (tw // multiple_of) * multiple_of
        th = (th // multiple_of) * multiple_of
        
        if method == "proportion":
            s = min(tw/w, th/h)
            tw, th = int(w*s), int(h*s)
        
        if mask is None: mask = torch.zeros((b, h, w), dtype=torch.float32, device=image.device)
        if mask.shape != (b, h, w): mask = F.interpolate(mask.unsqueeze(1), size=(h, w), mode="nearest").squeeze(1)

        if method in ["pad", "fill"]:
            s = min(tw/w, th/h) if method == "pad" else max(tw/w, th/h)
            nw, nh = int(w*s), int(h*s)
            img_r = F.interpolate(image.permute(0,3,1,2), size=(nh, nw), mode=interpolation if interpolation != "lanczos" else "bicubic")
            msk_r = F.interpolate(mask.unsqueeze(1), size=(nh, nw), mode="nearest")
            
            pad_w, pad_h = tw - nw, th - nh
            px, py = pad_w // 2, pad_h // 2
            if "top" in crop_pad_pos: py = 0
            elif "bottom" in crop_pad_pos: py = pad_h
            if "left" in crop_pad_pos: px = 0
            elif "right" in crop_pad_pos: px = pad_w
            
            if method == "pad":
                img_out = F.pad(img_r, (px, pad_w-px, py, pad_h-py), value=0)
                msk_out = F.pad(msk_r, (px, pad_w-px, py, pad_h-py), value=0)
            else:
                img_out = img_r[:, :, py:py+th, px:px+tw]
                msk_out = msk_r[:, :, py:py+th, px:px+tw]
        else:
            img_out = F.interpolate(image.permute(0,3,1,2), size=(th, tw), mode=interpolation if interpolation != "lanczos" else "bicubic")
            msk_out = F.interpolate(mask.unsqueeze(1), size=(th, tw), mode="nearest")

        return (img_out.permute(0,2,3,1), msk_out.squeeze(1), tw, th)
