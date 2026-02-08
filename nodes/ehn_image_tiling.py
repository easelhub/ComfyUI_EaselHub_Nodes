import torch
import torch.nn.functional as F

class EHN_ImageTiler:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {"image": ("IMAGE",), "tile_size": ("INT", {"default": 512, "min": 64, "max": 8192, "step": 64}), "overlap": ("INT", {"default": 64, "min": 0, "max": 512, "step": 8})}}
    RETURN_TYPES = ("IMAGE", "EHN_TILE_INFO")
    RETURN_NAMES = ("tiles", "tile_info")
    FUNCTION = "execute"
    CATEGORY = "EaselHub Nodes/Image"

    def execute(self, image, tile_size, overlap):
        B, H, W, C = image.shape
        tiles = []
        info = []
        step = tile_size - overlap
        if step <= 0: step = 1
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
                    h_end = min(y + tile_size, H)
                    w_end = min(x + tile_size, W)
                    crop = image[b, y:h_end, x:w_end, :]
                    h_act, w_act = crop.shape[:2]
                    pad_h = tile_size - h_act
                    pad_w = tile_size - w_act
                    if pad_h > 0 or pad_w > 0:
                        crop = crop.permute(2, 0, 1).unsqueeze(0)
                        crop = F.pad(crop, (0, pad_w, 0, pad_h), mode='reflect')
                        crop = crop.squeeze(0).permute(1, 2, 0)
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
        total_images = images.shape[0]
        if total_images % num_tiles != 0:
            raise ValueError(f"Image count {total_images} mismatch tile info {num_tiles}")
        batch_factor = total_images // num_tiles
        B_orig = max(t[0] for t in tile_info) + 1
        H_orig, W_orig, overlap = tile_info[0][5], tile_info[0][6], tile_info[0][7]
        B_out = B_orig * batch_factor
        C = images.shape[-1]
        device = images.device
        canvas = torch.zeros((B_out, H_orig, W_orig, C), device=device)
        weights = torch.zeros((B_out, H_orig, W_orig, C), device=device)
        for idx in range(total_images):
            info_idx = idx % num_tiles
            batch_iter = idx // num_tiles
            b_orig_idx, y, x, h_act, w_act, _, _, _ = tile_info[info_idx]
            b_target = b_orig_idx + (batch_iter * B_orig)
            tile = images[idx, :h_act, :w_act, :]
            mask_h = torch.ones(h_act, device=device)
            if y > 0 and overlap > 0:
                mask_h[:overlap] = torch.linspace(0, 1, overlap, device=device)
            if y + h_act < H_orig and overlap > 0:
                mask_h[-overlap:] = torch.linspace(1, 0, overlap, device=device)
            mask_w = torch.ones(w_act, device=device)
            if x > 0 and overlap > 0:
                mask_w[:overlap] = torch.linspace(0, 1, overlap, device=device)
            if x + w_act < W_orig and overlap > 0:
                mask_w[-overlap:] = torch.linspace(1, 0, overlap, device=device)
            mask = (mask_h[:, None] * mask_w[None, :])[:, :, None]
            canvas[b_target, y:y+h_act, x:x+w_act, :] += tile * mask
            weights[b_target, y:y+h_act, x:x+w_act, :] += mask
        return (canvas / (weights + 1e-8),)
