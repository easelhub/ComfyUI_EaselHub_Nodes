import torch
import torch.nn.functional as F
from .ehn_mask_ops import process_mask_core

class EHN_ImageResize:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "width": ("INT", {"default": 1024, "min": 0, "max": 16384, "step": 8}),
                "height": ("INT", {"default": 1024, "min": 0, "max": 16384, "step": 8}),
                "interpolation": (["nearest", "bilinear", "bicubic", "area"], {"default": "bicubic"}),
                "method": (["stretch", "keep proportion", "fill / crop", "pad"], {"default": "keep proportion"}),
                "condition": (["always", "downscale if bigger", "upscale if smaller", "if bigger area", "if smaller area"], {"default": "always"}),
                "multiple_of": ("INT", {"default": 0, "min": 0, "max": 512, "step": 8}),
                "mask_expansion": ("INT", {"default": 0, "min": -512, "max": 512, "step": 1}),
                "mask_blur": ("INT", {"default": 0, "min": 0, "max": 256, "step": 1}),
                "mask_fill_holes": ("BOOLEAN", {"default": False}),
                "mask_invert": ("BOOLEAN", {"default": False}),
            },
            "optional": {"mask": ("MASK",)}
        }
    RETURN_TYPES = ("IMAGE", "MASK")
    RETURN_NAMES = ("image", "mask")
    FUNCTION = "execute"
    CATEGORY = "EaselHub Nodes/Image"

    def execute(self, image, width, height, interpolation, method, condition, multiple_of, mask_expansion, mask_blur, mask_fill_holes, mask_invert, mask=None):
        B, H, W, C = image.shape
        
        if width == 0 and height == 0:
            m = mask if mask is not None else torch.ones((B, H, W), device=image.device, dtype=image.dtype)
            return (image, process_mask_core(m, mask_invert, mask_expansion, mask_blur, mask_fill_holes))

        tw, th = width, height
        if tw == 0: tw = max(1, round(W * th / H))
        elif th == 0: th = max(1, round(H * tw / W))

        if multiple_of > 1:
            tw = tw - (tw % multiple_of)
            th = th - (th % multiple_of)

        do_resize = True
        if condition == "downscale if bigger":
            if method == "fill / crop":
                if W <= tw and H <= th: do_resize = False
            elif W <= tw or H <= th: do_resize = False
        elif condition == "upscale if smaller":
            if method == "fill / crop":
                if W >= tw and H >= th: do_resize = False
            elif W >= tw or H >= th: do_resize = False
        elif condition == "if bigger area":
            if W * H <= tw * th: do_resize = False
        elif condition == "if smaller area":
            if W * H >= tw * th: do_resize = False

        if not do_resize:
            m = mask if mask is not None else torch.ones((B, H, W), device=image.device, dtype=image.dtype)
            return (image, process_mask_core(m, mask_invert, mask_expansion, mask_blur, mask_fill_holes))

        rw, rh = tw, th
        if method == "keep proportion" or method == "pad":
            s = min(tw / W, th / H)
            rw, rh = max(1, round(W * s)), max(1, round(H * s))
        elif method == "fill / crop":
            s = max(tw / W, th / H)
            rw, rh = max(1, round(W * s)), max(1, round(H * s))

        img = image.permute(0, 3, 1, 2)
        img = F.interpolate(img, size=(rh, rw), mode=interpolation)
        img = img.permute(0, 2, 3, 1)

        m = mask.unsqueeze(1) if mask is not None else torch.ones((B, 1, rh, rw), device=image.device, dtype=image.dtype)
        if mask is not None:
            m = F.interpolate(m, size=(rh, rw), mode="nearest")
        
        if method == "pad":
            pw, ph = tw - rw, th - rh
            pl, pt = pw // 2, ph // 2
            if pw > 0 or ph > 0:
                img = img.permute(0, 3, 1, 2)
                img = F.pad(img, (pl, pw - pl, pt, ph - pt), value=0)
                img = img.permute(0, 2, 3, 1)
                m = F.pad(m, (pl, pw - pl, pt, ph - pt), value=0)
        elif method == "fill / crop":
            cw, ch = rw - tw, rh - th
            cl, ct = cw // 2, ch // 2
            if cw > 0 or ch > 0:
                img = img[:, ct:ct+th, cl:cl+tw, :]
                m = m[:, :, ct:ct+th, cl:cl+tw]

        if mask is None and method != "pad":
             m = torch.ones((B, 1, img.shape[1], img.shape[2]), device=image.device, dtype=image.dtype)

        return (img, process_mask_core(m.squeeze(1), mask_invert, mask_expansion, mask_blur, mask_fill_holes))