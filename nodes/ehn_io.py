import os
import torch
import numpy as np
from PIL import Image, ImageOps
import random

class EHN_LoadImagesFromDir:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "directory": ("STRING", {"default": ""}),
                "start_index": ("INT", {"default": 0, "min": 0}),
                "batch_count": ("INT", {"default": 1, "min": 1, "max": 1000}),
                "sort_method": (["alphanumeric", "date_modified", "random_shuffle"],),
            },
            "optional": {
                 "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            }
        }

    RETURN_TYPES = ("IMAGE", "MASK", "STRING", "STRING", "INT", "INT")
    RETURN_NAMES = ("Images", "Masks", "Filenames", "Metadata_Prompt", "Width", "Height")
    OUTPUT_IS_LIST = (True, True, True, True, True, True)
    FUNCTION = "load_images"
    CATEGORY = "EaselHub/IO"

    @classmethod
    def IS_CHANGED(s, directory, sort_method, seed, **kwargs):
        if not os.path.isdir(directory): return ""
        mtime = os.path.getmtime(directory)
        if sort_method == "random_shuffle":
            return f"{directory}_{mtime}_{seed}"
        return f"{directory}_{mtime}"

    def load_images(self, directory, start_index, batch_count, sort_method, seed=0):
        if not directory or not os.path.isdir(directory):
            return ([], [], [], [], [], [])

        valid_exts = {'.png', '.jpg', '.jpeg', '.webp', '.bmp'}
        files = [f for f in os.listdir(directory) if os.path.splitext(f)[1].lower() in valid_exts]

        if sort_method == "alphanumeric":
            files.sort()
        elif sort_method == "date_modified":
            files.sort(key=lambda x: os.path.getmtime(os.path.join(directory, x)))
        elif sort_method == "random_shuffle":
            random.seed(seed)
            random.shuffle(files)

        total = len(files)
        if total == 0: return ([], [], [], [], [], [])
        
        # Collect batch
        out_imgs, out_masks, out_names, out_meta, out_w, out_h = [], [], [], [], [], []

        for i in range(batch_count):
            # Safe loop index
            idx = (start_index + i) % total
            fname = files[idx]
            path = os.path.join(directory, fname)
            
            try:
                img = Image.open(path)
                
                # Extract simple metadata string
                info = ""
                if hasattr(img, 'text') and img.text:
                    info = img.text.get('parameters', '') or img.text.get('workflow', '') or str(img.text)
                elif hasattr(img, 'info') and img.info:
                    info = str(img.info.get('parameters', ''))

                img = ImageOps.exif_transpose(img)
                w, h = img.size
                
                rgb = img.convert("RGB")
                img_np = np.array(rgb).astype(np.float32) / 255.0
                out_imgs.append(torch.from_numpy(img_np)[None,])
                
                if 'A' in img.getbands():
                    mask_np = np.array(img.getchannel('A')).astype(np.float32) / 255.0
                    mask = 1. - torch.from_numpy(mask_np)
                else:
                    mask = torch.zeros((h, w), dtype=torch.float32)
                out_masks.append(mask)
                
                out_names.append(fname)
                out_meta.append(info)
                out_w.append(w)
                out_h.append(h)

            except Exception as e:
                print(f"[EHN] Error loading {fname}: {e}")

        return (out_imgs, out_masks, out_names, out_meta, out_w, out_h)