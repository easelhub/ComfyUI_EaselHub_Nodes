import os
import random
import torch
import numpy as np
from PIL import Image, ImageOps

class EHN_ImageLoader:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "directory": ("STRING", {"default": ""}),
                "limit": ("INT", {"default": 0, "min": 0, "max": 10000}),
                "start": ("INT", {"default": 0, "min": 0, "max": 10000}),
                "recursive": ("BOOLEAN", {"default": False}),
                "sort": (["name_asc", "name_desc", "random"],),
            }
        }
    RETURN_TYPES = ("IMAGE", "MASK", "INT")
    RETURN_NAMES = ("images", "masks", "count")
    OUTPUT_IS_LIST = (True, True, False)
    FUNCTION = "run"
    CATEGORY = "EaselHub Nodes/Loader"

    def run(self, directory, limit, start, recursive, sort):
        if not os.path.isdir(directory): return ([], [], 0)
        exts = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff', '.gif'}
        files = []
        if recursive:
            for r, _, f in os.walk(directory):
                files.extend([os.path.join(r, x) for x in f if os.path.splitext(x)[1].lower() in exts])
        else:
            files = [os.path.join(directory, x) for x in os.listdir(directory) if os.path.splitext(x)[1].lower() in exts]
        
        if sort == "name_asc": files.sort()
        elif sort == "name_desc": files.sort(reverse=True)
        elif sort == "random": random.shuffle(files)
        
        files = files[start:]
        if limit > 0: files = files[:limit]
        if not files: return ([], [], 0)

        imgs, msks = [], []
        for f in files:
            try:
                i = ImageOps.exif_transpose(Image.open(f))
                if i.mode == 'I': i = i.point(lambda x: x * (1/255))
                i = i.convert("RGBA")
                m = i.split()[-1]
                i = i.convert("RGB")
                
                imgs.append(torch.from_numpy(np.array(i).astype(np.float32) / 255.0).unsqueeze(0))
                msks.append(1.0 - torch.from_numpy(np.array(m).astype(np.float32) / 255.0).unsqueeze(0))
            except: continue
            
        if not imgs: return ([], [], 0)
        return (imgs, msks, len(imgs))

    @classmethod
    def IS_CHANGED(s, sort, **kwargs):
        return float("NaN") if sort == "random" else ""
