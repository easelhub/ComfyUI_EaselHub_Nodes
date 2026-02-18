import torch
import torch.nn.functional as F

class EHN_ImageTileBatch:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {"image": ("IMAGE",), "tile_size": ("INT", {"default": 512, "min": 64, "max": 8192, "step": 8}), "overlap": ("INT", {"default": 64, "min": 0, "max": 512, "step": 8})}}
    RETURN_TYPES = ("IMAGE", "TILE_INFO")
    RETURN_NAMES = ("tiles", "tile_info")
    FUNCTION = "execute"
    CATEGORY = "EaselHub/Image"
    def execute(self, image, tile_size, overlap):
        B, H, W, C = image.shape
        if H <= tile_size and W <= tile_size: return (image, (tile_size, overlap, W, H))
        s = tile_size - overlap
        h_n = (H - tile_size + s - 1) // s + 1 if H > tile_size else 1
        w_n = (W - tile_size + s - 1) // s + 1 if W > tile_size else 1
        tiles = []
        for b in range(B):
            for i in range(h_n):
                y = min(i * s, H - tile_size) if H > tile_size else 0
                for j in range(w_n):
                    x = min(j * s, W - tile_size) if W > tile_size else 0
                    tiles.append(image[b:b+1, y:y+tile_size, x:x+tile_size, :])
        return (torch.cat(tiles, dim=0), (tile_size, overlap, W, H))

class EHN_ImageAssembly:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {"tiles": ("IMAGE",), "tile_info": ("TILE_INFO",), "blend": ("BOOLEAN", {"default": True})}}
    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "execute"
    CATEGORY = "EaselHub/Image"
    def execute(self, tiles, tile_info, blend):
        tile_size, overlap, original_width, original_height = tile_info
        T, TH, TW, C = tiles.shape
        if TH != tile_size or TW != tile_size: tiles = F.interpolate(tiles.movedim(-1,1), size=(tile_size, tile_size), mode='bilinear', align_corners=False).movedim(1,-1)
        B = T // (((original_height - tile_size + (tile_size - overlap) - 1) // (tile_size - overlap) + 1 if original_height > tile_size else 1) * ((original_width - tile_size + (tile_size - overlap) - 1) // (tile_size - overlap) + 1 if original_width > tile_size else 1))
        out = torch.zeros((B, original_height, original_width, C), device=tiles.device)
        wgt = torch.zeros((B, original_height, original_width, 1), device=tiles.device)
        m = torch.ones((tile_size, tile_size, 1), device=tiles.device)
        if blend and overlap > 0:
            x = torch.linspace(0, 1, overlap)
            m[:overlap, :, :] *= x.view(-1, 1, 1)
            m[-overlap:, :, :] *= x.flip(0).view(-1, 1, 1)
            m[:, :overlap, :] *= x.view(1, -1, 1)
            m[:, -overlap:, :] *= x.flip(0).view(1, -1, 1)
        s = tile_size - overlap
        h_n = (original_height - tile_size + s - 1) // s + 1 if original_height > tile_size else 1
        w_n = (original_width - tile_size + s - 1) // s + 1 if original_width > tile_size else 1
        idx = 0
        for b in range(B):
            for i in range(h_n):
                y = min(i * s, original_height - tile_size) if original_height > tile_size else 0
                for j in range(w_n):
                    x = min(j * s, original_width - tile_size) if original_width > tile_size else 0
                    if idx < T:
                        out[b:b+1, y:y+tile_size, x:x+tile_size, :] += tiles[idx] * m
                        wgt[b:b+1, y:y+tile_size, x:x+tile_size, :] += m
                        idx += 1
        return (out / torch.clamp(wgt, min=1e-5),)
