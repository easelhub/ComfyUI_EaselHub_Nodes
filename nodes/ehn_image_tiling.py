import torch
import torch.nn.functional as F

class EHN_ImageTiler:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "tile_size": ("INT", {"default": 1024, "min": 64, "max": 8192, "step": 64}),
            }
        }
    RETURN_TYPES = ("IMAGE", "EHN_TILE_INFO")
    RETURN_NAMES = ("tiles", "tile_info")
    FUNCTION = "execute"
    CATEGORY = "EaselHub Nodes/Image"

    def execute(self, image, tile_size):
        B, H, W, C = image.shape
        tiles, info = [], []
        overlap = tile_size // 4
        step = tile_size - overlap
        
        for b in range(B):
            y_starts = []
            y = 0
            while y < H:
                y_starts.append(y)
                if y + tile_size >= H: break
                y += step
            if y_starts[-1] + tile_size > H: y_starts[-1] = max(0, H - tile_size)
            
            x_starts = []
            x = 0
            while x < W:
                x_starts.append(x)
                if x + tile_size >= W: break
                x += step
            if x_starts[-1] + tile_size > W: x_starts[-1] = max(0, W - tile_size)
            
            for y in y_starts:
                for x in x_starts:
                    h_act, w_act = min(y + tile_size, H) - y, min(x + tile_size, W) - x
                    crop = image[b, y:y+h_act, x:x+w_act, :]
                    if h_act < tile_size or w_act < tile_size:
                        crop = F.pad(crop.permute(2, 0, 1).unsqueeze(0), (0, tile_size - w_act, 0, tile_size - h_act), mode='reflect').squeeze(0).permute(1, 2, 0)
                    tiles.append(crop)
                    info.append((b, y, x, h_act, w_act, H, W, overlap))
        return (torch.stack(tiles), info)

class EHN_ImageMerger:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {"images": ("IMAGE",), "tile_info": ("EHN_TILE_INFO",)}}
    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "execute"
    CATEGORY = "EaselHub Nodes/Image"

    def execute(self, images, tile_info):
        num_tiles = len(tile_info)
        if images.shape[0] % num_tiles != 0: raise ValueError("Image count mismatch")
        B_orig, H_orig, W_orig, overlap = max(t[0] for t in tile_info) + 1, tile_info[0][5], tile_info[0][6], tile_info[0][7]
        B_out = B_orig * (images.shape[0] // num_tiles)
        canvas = torch.zeros((B_out, H_orig, W_orig, images.shape[-1]), device=images.device)
        weights = torch.zeros_like(canvas)
        
        for idx in range(images.shape[0]):
            b_orig_idx, y, x, h_act, w_act, _, _, _ = tile_info[idx % num_tiles]
            b_target = b_orig_idx + ((idx // num_tiles) * B_orig)
            tile = images[idx, :h_act, :w_act, :]
            
            mask_h = torch.ones(h_act, device=images.device)
            if overlap > 0:
                if y > 0: mask_h[:overlap] = torch.linspace(0, 1, overlap, device=images.device)
                if y + h_act < H_orig: mask_h[-overlap:] = torch.linspace(1, 0, overlap, device=images.device)
            
            mask_w = torch.ones(w_act, device=images.device)
            if overlap > 0:
                if x > 0: mask_w[:overlap] = torch.linspace(0, 1, overlap, device=images.device)
                if x + w_act < W_orig: mask_w[-overlap:] = torch.linspace(1, 0, overlap, device=images.device)
                
            mask = (mask_h[:, None] * mask_w[None, :])[:, :, None]
            canvas[b_target, y:y+h_act, x:x+w_act, :] += tile * mask
            weights[b_target, y:y+h_act, x:x+w_act, :] += mask
            
        return (canvas / (weights + 1e-8),)