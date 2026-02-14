import torch
import torch.nn.functional as F
import comfy.utils
from nodes import MAX_RESOLUTION

class Easel_ImageResize:
    CATEGORY, RETURN_TYPES, RETURN_NAMES, FUNCTION = "EaselHub/Image", ("IMAGE", "MASK", "INT", "INT"), ("IMAGE", "MASK", "width", "height"), "execute"
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "image": ("IMAGE",),
            "width": ("INT", { "default": 512, "min": 0, "max": MAX_RESOLUTION, "step": 1 }),
            "height": ("INT", { "default": 512, "min": 0, "max": MAX_RESOLUTION, "step": 1 }),
            "interpolation": (["nearest", "bilinear", "bicubic", "area", "nearest-exact", "lanczos"],),
            "method": (["stretch", "keep proportion", "fill / crop", "pad"],),
            "condition": (["always", "downscale if bigger", "upscale if smaller", "if bigger area", "if smaller area"],),
            "multiple_of": ("INT", { "default": 0, "min": 0, "max": 512, "step": 1 }),
        }, "optional": {"mask": ("MASK",)}}
    
    def execute(self, image, width, height, method="stretch", interpolation="nearest", condition="always", multiple_of=0, mask=None):
        _, oh, ow, _ = image.shape
        x = y = x2 = y2 = 0
        pad_left = pad_right = pad_top = pad_bottom = 0
        if multiple_of > 1: width, height = width - (width % multiple_of), height - (height % multiple_of)
        if method == 'keep proportion' or method == 'pad':
            if width == 0: width = MAX_RESOLUTION if oh < height else ow
            if height == 0: height = MAX_RESOLUTION if ow < width else oh
            ratio = min(width / ow, height / oh)
            nw, nh = round(ow*ratio), round(oh*ratio)
            if method == 'pad':
                pad_left = (width - nw) // 2
                pad_right = width - nw - pad_left
                pad_top = (height - nh) // 2
                pad_bottom = height - nh - pad_top
            width, height = nw, nh
        elif method.startswith('fill'):
            width, height = (width if width > 0 else ow), (height if height > 0 else oh)
            ratio = max(width / ow, height / oh)
            nw, nh = round(ow*ratio), round(oh*ratio)
            x, y = (nw - width) // 2, (nh - height) // 2
            x2, y2 = x + width, y + height
            if x2 > nw: x -= (x2 - nw)
            if x < 0: x = 0
            if y2 > nh: y -= (y2 - nh)
            if y < 0: y = 0
            width, height = nw, nh
        else: width, height = (width if width > 0 else ow), (height if height > 0 else oh)
        
        out, out_mask = image, mask
        if "always" in condition or ("downscale" in condition and (oh > height or ow > width)) or ("upscale" in condition and (oh < height or ow < width)) or ("bigger area" in condition and (oh * ow > height * width)) or ("smaller area" in condition and (oh * ow < height * width)):
            out = image.permute(0,3,1,2)
            out = comfy.utils.lanczos(out, width, height) if interpolation == "lanczos" else F.interpolate(out, size=(height, width), mode=interpolation)
            if mask is not None:
                out_mask = mask.unsqueeze(1)
                out_mask = comfy.utils.lanczos(out_mask, width, height) if interpolation == "lanczos" else F.interpolate(out_mask, size=(height, width), mode=interpolation)
                out_mask = out_mask.squeeze(1)
            if method == 'pad' and any([pad_left, pad_right, pad_top, pad_bottom]):
                out = F.pad(out, (pad_left, pad_right, pad_top, pad_bottom), value=0)
                if out_mask is not None: out_mask = F.pad(out_mask, (pad_left, pad_right, pad_top, pad_bottom), value=0)
            out = out.permute(0,2,3,1)
            if method.startswith('fill') and any([x, y, x2, y2]):
                out = out[:, y:y2, x:x2, :]
                if out_mask is not None: out_mask = out_mask[:, y:y2, x:x2]
        
        if multiple_of > 1 and (out.shape[2] % multiple_of != 0 or out.shape[1] % multiple_of != 0):
            width, height = out.shape[2], out.shape[1]
            x, y = (width % multiple_of) // 2, (height % multiple_of) // 2
            x2, y2 = width - ((width % multiple_of) - x), height - ((height % multiple_of) - y)
            out = out[:, y:y2, x:x2, :]
            if out_mask is not None: out_mask = out_mask[:, y:y2, x:x2]
            
        return (torch.clamp(out, 0, 1), torch.clamp(out_mask, 0, 1) if out_mask is not None else None, out.shape[2], out.shape[1])
