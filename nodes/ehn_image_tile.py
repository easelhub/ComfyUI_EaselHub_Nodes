import torch, torch.nn.functional as F, math
from .ehn_utils import any_type

class EHN_ImageSplitTiles:
    @classmethod
    def INPUT_TYPES(s): return {"required": {"image":("IMAGE",), "tile_size":("INT",{"default":1024}), "overlap":("INT",{"default":64})}}
    RETURN_TYPES = ("IMAGE", any_type)
    RETURN_NAMES = ("tiles", "tile_info")
    FUNCTION = "split"
    CATEGORY = "EaselHub/Image"
    def split(self, image, tile_size, overlap):
        b, h, w, c = image.shape
        stride = tile_size - overlap
        if stride <= 0: raise ValueError("Overlap >= Tile Size")
        rows, cols = math.ceil((h-overlap)/stride), math.ceil((w-overlap)/stride)
        rows, cols = max(1, rows), max(1, cols)
        tw, th = (cols-1)*stride+tile_size, (rows-1)*stride+tile_size
        img_p = F.pad(image.permute(0,3,1,2), (0, max(0, tw-w), 0, max(0, th-h)), mode='reflect')
        tiles = []
        for r in range(rows):
            for c in range(cols):
                y, x = r*stride, c*stride
                tiles.append(img_p[:, :, y:y+tile_size, x:x+tile_size])
        out = torch.stack(tiles, dim=0).permute(1,0,2,3,4).reshape(-1, c, tile_size, tile_size)
        return (out.permute(0,2,3,1), {"orig_w":w, "orig_h":h, "tile_size":tile_size, "overlap":overlap, "rows":rows, "cols":cols, "batch":b})

class EHN_ImageMergeTiles:
    @classmethod
    def INPUT_TYPES(s): return {"required": {"images":("IMAGE",), "tile_info":(any_type,)}}
    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "merge"
    CATEGORY = "EaselHub/Image"
    def merge(self, images, tile_info):
        t_cnt, th, tw, c = images.shape
        ow, oh, rs, cs, bat = tile_info["orig_w"], tile_info["orig_h"], tile_info["rows"], tile_info["cols"], tile_info.get("batch", 1)
        scale = tw / tile_info["tile_size"]
        ov, strd = int(tile_info["overlap"]*scale), int(tw - int(tile_info["overlap"]*scale))
        fw, fh = (cs-1)*strd + tw, (rs-1)*strd + th
        
        dev = images.device
        yr, xr = torch.linspace(0,1,th,device=dev), torch.linspace(0,1,tw,device=dev)
        wm = (torch.min(yr, yr.flip(0))*2*(th/(ov*2+1e-6))).clamp(0,1)[:,None] * (torch.min(xr, xr.flip(0))*2*(tw/(ov*2+1e-6))).clamp(0,1)[None,:]
        wm = (wm*wm*(3-2*wm))[None,None]
        
        out = []
        img_c = images.permute(0,3,1,2)
        for b in range(bat):
            cnv = torch.zeros((c, fh, fw), device=dev)
            wmap = torch.zeros((1, fh, fw), device=dev)
            off = b * rs * cs
            idx = 0
            for r in range(rs):
                for c_ in range(cs):
                    if idx >= rs*cs or off+idx >= t_cnt: break
                    y, x = r*strd, c_*strd
                    t = img_c[off+idx].unsqueeze(0)
                    cnv[:, y:y+th, x:x+tw] += (t*wm)[0]
                    wmap[:, y:y+th, x:x+tw] += wm[0]
                    idx += 1
            fin = cnv / wmap.clamp(min=1e-5)
            out.append(fin[:, :int(oh*scale), :int(ow*scale)].permute(1,2,0).unsqueeze(0))
        return (torch.cat(out, 0) if out else torch.zeros((1,512,512,3)),)