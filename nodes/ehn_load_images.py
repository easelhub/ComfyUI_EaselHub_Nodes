import os, torch, numpy as np, random
from PIL import Image, ImageOps

class EHN_LoadImagesFromDir:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {"directory": ("STRING", {}), "start_index": ("INT", {"default": 0}), "batch_count": ("INT", {"default": 99}), "recursive": ("BOOLEAN", {"default": False})}, "optional": {"filter_filename": ("STRING", {})}}
    RETURN_TYPES = ("IMAGE", "MASK", "STRING", "STRING", "INT", "INT")
    RETURN_NAMES = ("Images", "Masks", "Filenames", "Metadata", "Widths", "Heights")
    OUTPUT_IS_LIST = (True, True, True, True, True, True)
    FUNCTION = "load"
    CATEGORY = "EaselHub/IO"
    DESCRIPTION = "Batch loads images from a directory with filtering and recursion support."

    @classmethod
    def IS_CHANGED(s, directory, recursive, filter_filename, **kwargs):
        if not os.path.isdir(directory): return ""
        return f"{directory}_{os.path.getmtime(directory)}"

    def load(self, directory, start_index, batch_count, recursive, filter_filename=""):
        if not directory or not os.path.isdir(directory): return ([],[],[],[],[],[])
        exts = {'.png', '.jpg', '.jpeg', '.webp', '.bmp'}
        files = []
        if recursive:
            for r, _, fs in os.walk(directory):
                files.extend(os.path.join(r, f) for f in fs if os.path.splitext(f)[1].lower() in exts)
        else:
            files = [os.path.join(directory, f) for f in os.listdir(directory) if os.path.splitext(f)[1].lower() in exts]
        
        if filter_filename: files = [f for f in files if filter_filename.lower() in os.path.basename(f).lower()]
        
        files.sort()

        if not files: return ([],[],[],[],[],[])
        
        imgs, msks, names, meta, ws, hs = [], [], [], [], [], []
        cnt = min(batch_count, len(files))
        
        for i in range(cnt):
            path = files[(start_index + i) % len(files)]
            try:
                img = ImageOps.exif_transpose(Image.open(path))
                imgs.append(torch.from_numpy(np.array(img.convert("RGB")).astype(np.float32)/255.0).unsqueeze(0))
                msks.append((1. - torch.from_numpy(np.array(img.getchannel('A')).astype(np.float32)/255.0).unsqueeze(0)) if 'A' in img.getbands() else torch.zeros((img.size[1], img.size[0]), dtype=torch.float32).unsqueeze(0))
                names.append(os.path.basename(path))
                meta.append(str(img.info.get('parameters', '')))
                ws.append(img.size[0]); hs.append(img.size[1])
            except: pass
        return (imgs, msks, names, meta, ws, hs)