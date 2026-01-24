import torch
import torch.nn.functional as F
import math
from .ehn_utils import any_type

# --- Resize & Crop ---
class EHN_ImageResize:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "width": ("INT", {"default": 0, "min": 0, "max": 16384}),
                "height": ("INT", {"default": 0, "min": 0, "max": 16384}),
                "target_mp": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 100.0, "step": 0.1}), 
                "interpolation": (["nearest", "bilinear", "bicubic", "area"], {"default": "bicubic"}),
                "method": ([
                    "stretch", 
                    "keep proportion", 
                    "fill / crop", 
                    "pad (letterbox)",
                    "scale to Target MP (Maintain Ratio)"
                ], {"default": "stretch"}),
                "condition": (["always", "downscale only", "upscale only"], {"default": "always"}),
                "multiple_of": ("INT", {"default": 0, "min": 0, "max": 512}),
            },
            "optional": { "mask": ("MASK",) }
        }

    RETURN_TYPES = ("IMAGE", "MASK", "INT", "INT")
    RETURN_NAMES = ("image", "mask", "width", "height")
    FUNCTION = "execute"
    CATEGORY = "EaselHub/Image"

    def execute(self, image, width, height, target_mp, interpolation, method, condition, multiple_of, mask=None):
        b, h, w, c = image.shape
        target_w, target_h = width, height

        # Logic: MP Scaling overrides dims
        if method == "scale to Target MP (Maintain Ratio)":
            current_pixels = w * h
            desired_pixels = target_mp * 1_000_000
            scale = math.sqrt(desired_pixels / (current_pixels + 1e-6))
            target_w = int(w * scale)
            target_h = int(h * scale)
            calc_method = "direct_calc" 
        else:
            calc_method = method
            if width == 0 and height == 0: target_w, target_h = w, h
            elif width == 0: target_w = int(w * (height / h))
            elif height == 0: target_h = int(h * (width / w))

        rw, rh = target_w, target_h
        
        if calc_method != "direct_calc":
            scale_w = target_w / w
            scale_h = target_h / h
            if method == "keep proportion":
                scale = min(scale_w, scale_h)
                rw, rh = int(w * scale), int(h * scale)
            elif method == "fill / crop":
                scale = max(scale_w, scale_h)
                rw, rh = int(w * scale), int(h * scale)
            elif method == "pad (letterbox)":
                scale = min(scale_w, scale_h)
                rw, rh = int(w * scale), int(h * scale)

        # Alignment
        if multiple_of > 1:
            rw = max(multiple_of, (rw // multiple_of) * multiple_of)
            rh = max(multiple_of, (rh // multiple_of) * multiple_of)
            if method == "stretch": target_w, target_h = rw, rh

        # Conditions
        should_run = False
        if condition == "always": should_run = True
        elif condition == "downscale only" and (rw < w or rh < h): should_run = True
        elif condition == "upscale only" and (rw > w or rh > h): should_run = True

        if mask is None:
            mask = torch.zeros((b, h, w), device=image.device, dtype=torch.float32)
        elif mask.dim() == 2:
            mask = mask.unsqueeze(0).repeat(b, 1, 1)

        if not should_run:
            return (image, mask, w, h)

        # Do Resize
        img_p = image.permute(0, 3, 1, 2)
        mask_p = mask.unsqueeze(1)
        img_res = F.interpolate(img_p, size=(rh, rw), mode=interpolation)
        mask_mode = "nearest" if interpolation == "nearest" else "bilinear"
        mask_res = F.interpolate(mask_p, size=(rh, rw), mode=mask_mode)

        # Post Process
        if method == "fill / crop":
            if rw > target_w:
                x = (rw - target_w) // 2
                img_res = img_res[..., x : x + target_w]
                mask_res = mask_res[..., x : x + target_w]
            if rh > target_h:
                y = (rh - target_h) // 2
                img_res = img_res[..., y : y + target_h, :]
                mask_res = mask_res[..., y : y + target_h, :]
        elif method == "pad (letterbox)":
            pad_w, pad_h = target_w - rw, target_h - rh
            if pad_w > 0 or pad_h > 0:
                pl, pt = pad_w // 2, pad_h // 2
                img_res = F.pad(img_res, (pl, pad_w - pl, pt, pad_h - pt))
                mask_res = F.pad(mask_res, (pl, pad_w - pl, pt, pad_h - pt))

        return (img_res.permute(0, 2, 3, 1), mask_res.squeeze(1), img_res.shape[3], img_res.shape[2])

# --- Tiling (Split) ---
class EHN_ImageSplitTiles:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "tile_size": ("INT", {"default": 512, "min": 128, "max": 8192, "step": 64}),
                "overlap": ("INT", {"default": 64, "min": 0, "max": 512, "step": 8}),
            }
        }

    RETURN_TYPES = ("IMAGE", any_type)
    RETURN_NAMES = ("tiles", "tile_info")
    FUNCTION = "split_image"
    CATEGORY = "EaselHub/Image"

    def split_image(self, image, tile_size, overlap):
        _, h, w, _ = image.shape
        stride = tile_size - overlap
        if stride <= 0: raise ValueError("Overlap must be smaller than Tile Size")

        rows = math.ceil((h - overlap) / stride)
        cols = math.ceil((w - overlap) / stride)
        rows, cols = max(1, rows), max(1, cols)

        target_w = (cols - 1) * stride + tile_size
        target_h = (rows - 1) * stride + tile_size
        pad_w, pad_h = target_w - w, target_h - h
        
        img_p = image.permute(0, 3, 1, 2)
        if pad_w > 0 or pad_h > 0:
            img_p = F.pad(img_p, (0, max(0, pad_w), 0, max(0, pad_h)), mode='reflect')
            
        tiles = []
        for r in range(rows):
            for c in range(cols):
                y, x = r * stride, c * stride
                tile = img_p[:, :, y:y+tile_size, x:x+tile_size]
                tiles.append(tile.permute(0, 2, 3, 1))

        return (torch.cat(tiles, dim=0), {
            "orig_w": w, "orig_h": h, "tile_size": tile_size, "overlap": overlap,
            "rows": rows, "cols": cols, "batch_size": image.shape[0]
        })

# --- Tiling (Merge) ---
class EHN_ImageMergeTiles:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE",),
                "tile_info": (any_type,),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "merge"
    CATEGORY = "EaselHub/Image"

    def merge(self, images, tile_info):
        total_tiles, t_h, t_w, C = images.shape
        orig_w, orig_h = tile_info["orig_w"], tile_info["orig_h"]
        rows, cols = tile_info["rows"], tile_info["cols"]
        orig_batch = tile_info.get("batch_size", 1)
        
        scale_factor = t_w / tile_info["tile_size"]
        overlap = int(tile_info["overlap"] * scale_factor)
        stride = t_w - overlap
        final_w = (cols - 1) * stride + t_w
        final_h = (rows - 1) * stride + t_h
        
        device = images.device
        
        # Smooth Blending Weight Mask
        y_ramp = torch.linspace(0, 1, t_h, device=device)
        y_weight = torch.clamp(torch.min(y_ramp, y_ramp.flip(0)) * 2.0 * (t_h / (overlap * 2 + 1e-6)), 0, 1)
        x_ramp = torch.linspace(0, 1, t_w, device=device)
        x_weight = torch.clamp(torch.min(x_ramp, x_ramp.flip(0)) * 2.0 * (t_w / (overlap * 2 + 1e-6)), 0, 1)
        
        weight_mask = (y_weight[:, None] * x_weight[None, :])
        weight_mask = weight_mask * weight_mask * (3 - 2 * weight_mask) # Smoothstep
        weight_mask = weight_mask.unsqueeze(0).unsqueeze(0) # [1, 1, H, W]
        
        output_batch_list = []
        images_c = images.permute(0, 3, 1, 2)
        
        for b_idx in range(orig_batch):
            canvas = torch.zeros((C, final_h, final_w), device=device)
            weight_map = torch.zeros((1, final_h, final_w), device=device)
            
            batch_offset = b_idx * (rows * cols)
            idx = 0
            for r in range(rows):
                for c in range(cols):
                    if idx >= (rows * cols): break
                    current_img_idx = batch_offset + idx
                    if current_img_idx >= total_tiles: break

                    y, x = r * stride, c * stride
                    tile = images_c[current_img_idx].unsqueeze(0)
                    
                    canvas[:, y:y+t_h, x:x+t_w] += (tile * weight_mask).squeeze(0)
                    weight_map[:, y:y+t_h, x:x+t_w] += weight_mask.squeeze(0)
                    idx += 1
            
            final_img = canvas / torch.clamp(weight_map, min=1e-5)
            target_out_w = int(orig_w * scale_factor)
            target_out_h = int(orig_h * scale_factor)
            output_batch_list.append(final_img[:, :target_out_h, :target_out_w].permute(1, 2, 0).unsqueeze(0))

        if not output_batch_list: return (torch.zeros((1, 512, 512, 3)),)
        return (torch.cat(output_batch_list, dim=0),)