import torch
import torch.nn.functional as F

class EHN_ImageTiler:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "tile_size": ("INT", {"default": 512, "min": 64, "max": 8192, "step": 64}),
                "overlap": ("INT", {"default": 64, "min": 0, "max": 256, "step": 8}),
            }
        }
    RETURN_TYPES = ("IMAGE", "EHN_TILE_INFO")
    RETURN_NAMES = ("tiles", "tile_info")
    FUNCTION = "execute"
    CATEGORY = "EaselHub Nodes/Image"
    def execute(self, image, tile_size, overlap):
        B, H, W, C = image.shape
        tiles, info = [], []
        stride = tile_size - overlap
        for b in range(B):
            y_steps = range(0, H - overlap, stride) if H > tile_size else [0]
            x_steps = range(0, W - overlap, stride) if W > tile_size else [0]
            for y in y_steps:
                for x in x_steps:
                    h_end = min(y + tile_size, H)
                    w_end = min(x + tile_size, W)
                    h_real, w_real = h_end - y, w_end - x
                    crop = image[b, y:h_end, x:w_end, :]
                    if h_real < tile_size or w_real < tile_size:
                        pad = (0, 0, 0, tile_size - w_real, 0, tile_size - h_real)
                        crop = F.pad(crop.permute(2, 0, 1), pad[2:], mode='constant', value=0).permute(1, 2, 0)
                    tiles.append(crop)
                    info.append((b, y, x, h_real, w_real, H, W, overlap))
        return (torch.stack(tiles), info)

class EHN_ImageMerger:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {"images": ("IMAGE",), "tile_info": ("EHN_TILE_INFO",)}}
    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "execute"
    CATEGORY = "EaselHub Nodes/Image"
    def execute(self, images, tile_info):
        if not tile_info: return (images,)
        B_orig, H, W, overlap = tile_info[0][5], tile_info[0][6], tile_info[0][7], tile_info[0][7]
        num_tiles = len(tile_info)
        B_out = images.shape[0] // num_tiles
        canvas = torch.zeros((B_out, H, W, images.shape[-1]), device=images.device)
        mask_acc = torch.zeros((B_out, H, W, 1), device=images.device)
        
        for i, (b_idx, y, x, h, w, _, _, _) in enumerate(tile_info):
            for b_out in range(B_out):
                tile = images[i + b_out * num_tiles, :h, :w, :]
                mask = torch.ones((h, w, 1), device=images.device)
                if overlap > 0:
                    edge = torch.linspace(0, 1, overlap, device=images.device)
                    if y > 0: mask[:overlap, :, :] *= edge.view(-1, 1, 1)
                    if y + h < H: mask[-overlap:, :, :] *= edge.flip(0).view(-1, 1, 1)
                    if x > 0: mask[:, :overlap, :] *= edge.view(1, -1, 1)
                    if x + w < W: mask[:, -overlap:, :] *= edge.flip(0).view(1, -1, 1)
                
                canvas[b_out, y:y+h, x:x+w, :] += tile * mask
                mask_acc[b_out, y:y+h, x:x+w, :] += mask
                
        return (canvas / (mask_acc + 1e-6),)