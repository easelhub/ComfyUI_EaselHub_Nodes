import torch
import torch.nn.functional as F

class EHN_ImageTiler:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "tile_size": ("INT", {"default": 1024, "min": 64, "max": 8192, "step": 8}),
                "overlap": ("INT", {"default": 128, "min": 0, "max": 512, "step": 8}),
            }
        }

    RETURN_TYPES = ("IMAGE", "TILE_INFO")
    RETURN_NAMES = ("tiles", "tile_info")
    FUNCTION = "execute"
    CATEGORY = "EaselHub/Image"

    def execute(self, image, tile_size, overlap):
        B, H, W, C = image.shape
        
        if H < tile_size: tile_size = H
        if W < tile_size: tile_size = W
        
        if overlap >= tile_size:
            overlap = max(0, tile_size - 8)
        
        h_step = tile_size - overlap
        w_step = tile_size - overlap
        
        h_starts = []
        curr_h = 0
        while curr_h + tile_size <= H:
            h_starts.append(curr_h)
            curr_h += h_step
        if not h_starts or h_starts[-1] + tile_size < H:
            h_starts.append(max(0, H - tile_size))
            
        w_starts = []
        curr_w = 0
        while curr_w + tile_size <= W:
            w_starts.append(curr_w)
            curr_w += w_step
        if not w_starts or w_starts[-1] + tile_size < W:
            w_starts.append(max(0, W - tile_size))
            
        tiles = []
        coords = []
        
        for h in h_starts:
            for w in w_starts:
                tile = image[:, h:h+tile_size, w:w+tile_size, :]
                tiles.append(tile)
                coords.append([h, w])
                
        if not tiles:
            return (image, {"original_shape": image.shape, "tile_size": tile_size, "overlap": overlap, "coords": []})

        tiles = torch.cat(tiles, dim=0)
        
        info = {
            "original_shape": (B, H, W, C),
            "tile_size": tile_size,
            "overlap": overlap,
            "coords": coords
        }
        
        return (tiles, info)

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
        tile_size = tile_info["tile_size"]
        overlap = tile_info["overlap"]
        coords = tile_info["coords"]
        
        output = torch.zeros((B, H, W, C), device=tiles.device)
        weight_map = torch.zeros((B, H, W, C), device=tiles.device)
        
        base_mask = torch.ones((tile_size, tile_size), device=tiles.device)
        
        if feather_mask and overlap > 0:
            t = torch.linspace(0, 1, overlap, device=tiles.device)
            ramp = t * t * (3 - 2 * t) 
            
            mask_x = torch.ones((tile_size, tile_size), device=tiles.device)
            mask_x[:, :overlap] = ramp.view(1, -1)
            mask_x[:, -overlap:] = (1 - ramp).view(1, -1)
            
            mask_y = torch.ones((tile_size, tile_size), device=tiles.device)
            mask_y[:overlap, :] = ramp.view(-1, 1)
            mask_y[-overlap:, :] = (1 - ramp).view(-1, 1)
            
            base_mask = mask_x * mask_y

        base_mask = base_mask.view(1, tile_size, tile_size, 1)

        for i, (h, w) in enumerate(coords):
            curr_mask = base_mask.clone()
            
            if h == 0: curr_mask[:, :overlap, :, :] = 1
            if h + tile_size == H: curr_mask[:, -overlap:, :, :] = 1
            if w == 0: curr_mask[:, :, :overlap, :] = 1
            if w + tile_size == W: curr_mask[:, :, -overlap:, :] = 1
            
            tile_batch = tiles[i*B : (i+1)*B]
            
            output[:, h:h+tile_size, w:w+tile_size, :] += tile_batch * curr_mask
            weight_map[:, h:h+tile_size, w:w+tile_size, :] += curr_mask
            
        return (output / (weight_map + 1e-6),)
