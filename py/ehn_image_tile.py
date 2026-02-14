import torch, numpy as np
from PIL import Image

class EHN_ImageTileBatch:
    CATEGORY, RETURN_TYPES, RETURN_NAMES, FUNCTION = "EaselHub/Image", ("IMAGE", "LIST", "TUPLE", "TUPLE"), ("IMAGES", "POSITIONS", "ORIGINAL_SIZE", "GRID_SIZE"), "tile"
    @classmethod
    def INPUT_TYPES(s): return {"required": {"image": ("IMAGE",), "tile_width": ("INT", {"default": 1024}), "tile_height": ("INT", {"default": 1024})}}
    def tile(self, image, tile_width, tile_height):
        img = Image.fromarray(np.clip(255. * image[0].cpu().numpy(), 0, 255).astype(np.uint8))
        w, h = img.size
        cols, rows = (w + tile_width - 1) // tile_width, (h + tile_height - 1) // tile_height
        tiles, pos = [], []
        for y in range(rows):
            for x in range(cols):
                l, u = x * tile_width, y * tile_height
                r, b = min(l + tile_width, w), min(u + tile_height, h)
                tiles.append(torch.from_numpy(np.array(img.crop((l, u, r, b))).astype(np.float32) / 255.).unsqueeze(0))
                pos.append((l, u, r, b))
        return (torch.cat(tiles), pos, (w, h), (cols, rows))

class EHN_ImageAssembly:
    CATEGORY, RETURN_TYPES, RETURN_NAMES, FUNCTION = "EaselHub/Image", ("IMAGE",), ("RECONSTRUCTED_IMAGE",), "assemble"
    @classmethod
    def INPUT_TYPES(s): return {"required": {"tiles": ("IMAGE",), "positions": ("LIST",), "original_size": ("TUPLE",), "grid_size": ("TUPLE",), "padding": ("INT", {"default": 64})}}
    def assemble(self, tiles, positions, original_size, grid_size, padding):
        res = Image.new("RGB", original_size)
        for i, (l, u, r, b) in enumerate(positions):
            t = Image.fromarray(np.clip(255. * tiles[i].cpu().numpy(), 0, 255).astype(np.uint8))
            res.paste(t, (l, u))
        return (torch.from_numpy(np.array(res).astype(np.float32) / 255.).unsqueeze(0),)
