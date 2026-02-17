import torch
import torch.nn.functional as F
import comfy.utils
from nodes import MAX_RESOLUTION

class EHN_ImageResize:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "width": ("INT", {"default": 1024, "min": 0, "max": MAX_RESOLUTION, "step": 8}),
                "height": ("INT", {"default": 1024, "min": 0, "max": MAX_RESOLUTION, "step": 8}),
                "upscale_method": (["nearest-exact", "bilinear", "area", "bicubic", "lanczos"], {"default": "nearest-exact"}),
                "resize_mode": (["stretch", "keep_ratio", "fill_crop", "pad"], {"default": "keep_ratio"}),
                "condition": (["always", "downscale_only", "upscale_only"], {"default": "always"}),
                "multiple_of": ("INT", {"default": 8, "min": 0, "max": 512, "step": 1})
            },
            "optional": {"mask": ("MASK",)}
        }

    RETURN_TYPES = ("IMAGE", "MASK", "INT", "INT")
    RETURN_NAMES = ("image", "mask", "width", "height")
    FUNCTION = "execute"
    CATEGORY = "EaselHub/Image"

    def execute(self, image, width, height, upscale_method="nearest-exact", resize_mode="keep_ratio", condition="always", multiple_of=8, mask=None):
        B, H, W, C = image.shape
        if multiple_of > 1 and width > 0 and height > 0:
            width = width - (width % multiple_of)
            height = height - (height % multiple_of)
        
        oh, ow = H, W
        if resize_mode == 'keep_ratio':
            r = min(width / W, height / H) if width > 0 and height > 0 else (width/W if width>0 else height/H)
            width, height = round(W * r), round(H * r)
        elif resize_mode == 'pad':
            r = min(width / W, height / H)
            nw, nh = round(W * r), round(H * r)
            pad_l, pad_t = (width - nw) // 2, (height - nh) // 2
            pad_r, pad_b = width - nw - pad_l, height - nh - pad_t
            width, height = nw, nh 
        elif resize_mode == 'fill_crop':
            r = max(width / W, height / H)
            nw, nh = round(W * r), round(H * r)
            crop_x, crop_y = (nw - width) // 2, (nh - height) // 2
            width, height = nw, nh

        if "always" not in condition:
            if ("downscale_only" == condition and (H < height or W < width)) or ("upscale_only" == condition and (H > height or W > width)):
                return (image, mask, W, H)

        img = image.permute(0, 3, 1, 2)
        if upscale_method == "lanczos":
            img = comfy.utils.lanczos(img, width, height)
        else:
            img = F.interpolate(img, size=(height, width), mode=upscale_method)
        
        if mask is not None:
            msk = mask.unsqueeze(1)
            if upscale_method == "lanczos":
                msk = comfy.utils.lanczos(msk, width, height)
            else:
                msk = F.interpolate(msk, size=(height, width), mode=upscale_method)
            msk = msk.squeeze(1)
        else:
            msk = None

        if resize_mode == 'pad':
            img = F.pad(img, (pad_l, pad_r, pad_t, pad_b), value=0)
            if msk is not None: msk = F.pad(msk, (pad_l, pad_r, pad_t, pad_b), value=0)
            width += pad_l + pad_r
            height += pad_t + pad_b
        
        img = img.permute(0, 2, 3, 1)

        if resize_mode == 'fill_crop':
            img = img[:, crop_y:crop_y + height - ((nh - height) if nh > height else 0), crop_x:crop_x + width - ((nw - width) if nw > width else 0), :]
            if msk is not None: msk = msk[:, crop_y:crop_y + height - ((nh - height) if nh > height else 0), crop_x:crop_x + width - ((nw - width) if nw > width else 0)]
            width = img.shape[2]
            height = img.shape[1]

        if multiple_of > 1:
            h, w = img.shape[1], img.shape[2]
            if h % multiple_of != 0 or w % multiple_of != 0:
                 img = img[:, :h - (h % multiple_of), :w - (w % multiple_of), :]
                 if msk is not None: msk = msk[:, :h - (h % multiple_of), :w - (w % multiple_of)]
                 width, height = img.shape[2], img.shape[1]

        return (torch.clamp(img, 0, 1), torch.clamp(msk, 0, 1) if msk is not None else None, width, height)
