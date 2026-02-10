import torch

class EHN_ImageTiler:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "tile_size": ("INT", {"default": 512, "min": 64, "max": 8192, "step": 8}),
                "overlap": ("INT", {"default": 64, "min": 0, "max": 512, "step": 8}),
            }
        }
    RETURN_TYPES = ("IMAGE", "TILE_INFO")
    RETURN_NAMES = ("tiles", "tile_info")
    FUNCTION = "execute"
    CATEGORY = "EaselHub/Image"

    def execute(self, image, tile_size, overlap):
        B, H, W, C = image.shape
        tile_size = min(tile_size, H, W)
        overlap = max(0, min(overlap, tile_size - 8))
        step = tile_size - overlap
        h_starts = list(range(0, H - tile_size + 1, step))
        if not h_starts or h_starts[-1] + tile_size < H: h_starts.append(max(0, H - tile_size))
        w_starts = list(range(0, W - tile_size + 1, step))
        if not w_starts or w_starts[-1] + tile_size < W: w_starts.append(max(0, W - tile_size))
        tiles, coords = [], []
        for h in h_starts:
            for w in w_starts:
                tiles.append(image[:, h:h+tile_size, w:w+tile_size, :])
                coords.append([h, w])
        return (torch.cat(tiles, dim=0), {"original_shape": (B, H, W, C), "tile_size": tile_size, "overlap": overlap, "coords": coords})

class EHN_ImageMerger:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "tiles": ("IMAGE",),
                "tile_info": ("TILE_INFO",),
                "feather_mask": ("BOOLEAN", {"default": True}),
            }
        }
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "execute"
    CATEGORY = "EaselHub/Image"

    def execute(self, tiles, tile_info, feather_mask):
        B, H, W, C = tile_info["original_shape"]
        tile_size, overlap, coords = tile_info["tile_size"], tile_info["overlap"], tile_info["coords"]
        output = torch.zeros((B, H, W, C), device=tiles.device)
        weight_map = torch.zeros((B, H, W, C), device=tiles.device)
        base_mask = torch.ones((tile_size, tile_size), device=tiles.device)
        if feather_mask and overlap > 0:
            t = torch.linspace(0, 1, overlap, device=tiles.device)
            ramp = t * t * (3 - 2 * t)
            mask_x = torch.ones((tile_size, tile_size), device=tiles.device)
            mask_x[:, :overlap], mask_x[:, -overlap:] = ramp.view(1, -1), (1 - ramp).view(1, -1)
            mask_y = torch.ones((tile_size, tile_size), device=tiles.device)
            mask_y[:overlap, :], mask_y[-overlap:, :] = ramp.view(-1, 1), (1 - ramp).view(-1, 1)
            base_mask = mask_x * mask_y
        base_mask = base_mask.view(1, tile_size, tile_size, 1)
        for i, (h, w) in enumerate(coords):
            curr_mask = base_mask.clone()
            if h == 0: curr_mask[:, :overlap, :, :] = 1
            if h + tile_size == H: curr_mask[:, -overlap:, :, :] = 1
            if w == 0: curr_mask[:, :, :overlap, :] = 1
            if w + tile_size == W: curr_mask[:, :, -overlap:, :] = 1
            output[:, h:h+tile_size, w:w+tile_size, :] += tiles[i*B:(i+1)*B] * curr_mask
            weight_map[:, h:h+tile_size, w:w+tile_size, :] += curr_mask
        return (output / (weight_map + 1e-6),)
