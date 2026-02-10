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
                "image_limit": ("INT", {"default": 0, "min": 0, "max": 10000}),
                "start_index": ("INT", {"default": 0, "min": 0, "max": 10000}),
                "recursive": ("BOOLEAN", {"default": False}),
                "sort_method": (["filename_asc", "filename_desc", "random"],),
            }
        }
    RETURN_TYPES = ("IMAGE", "MASK", "INT")
    RETURN_NAMES = ("images", "masks", "count")
    FUNCTION = "load_images"
    CATEGORY = "EaselHub Nodes/Loader"

    def load_images(self, directory, image_limit, start_index, recursive, sort_method):
        if not os.path.isdir(directory): raise FileNotFoundError(f"Directory not found: {directory}")
        file_paths = []
        valid_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff', '.gif'}
        if recursive:
            for root, _, files in os.walk(directory):
                for file in files:
                    if os.path.splitext(file)[1].lower() in valid_extensions: file_paths.append(os.path.join(root, file))
        else:
            file_paths = [os.path.join(directory, f) for f in os.listdir(directory) if os.path.splitext(f)[1].lower() in valid_extensions]
        
        if sort_method == "filename_asc": file_paths.sort()
        elif sort_method == "filename_desc": file_paths.sort(reverse=True)
        elif sort_method == "random": random.shuffle(file_paths)

        if start_index >= len(file_paths): return (torch.zeros((1, 64, 64, 3)), torch.zeros((1, 64, 64)), 0)

        limit = image_limit if image_limit > 0 else len(file_paths)
        selected_files = file_paths[start_index:start_index + limit]
        images, masks = [], []
        first_size = None

        for file_path in selected_files:
            try:
                img = ImageOps.exif_transpose(Image.open(file_path))
                if img.mode == 'I': img = img.point(lambda i: i * (1 / 255))
                if 'A' in img.getbands(): mask = 1. - np.array(img.getchannel('A')).astype(np.float32) / 255.0
                else: mask = np.zeros((img.height, img.width), dtype=np.float32)
                img = img.convert("RGB")
                if not first_size: first_size = img.size
                else:
                    if img.size != first_size:
                        img = img.resize(first_size, Image.BILINEAR)
                        mask = torch.nn.functional.interpolate(torch.from_numpy(mask).unsqueeze(0).unsqueeze(0), size=(first_size[1], first_size[0]), mode="bilinear", align_corners=False).squeeze().numpy()
                images.append(torch.from_numpy(np.array(img)).float() / 255.0)
                masks.append(torch.from_numpy(mask))
            except: continue

        if not images: return (torch.zeros((1, 64, 64, 3)), torch.zeros((1, 64, 64)), 0)
        return (torch.stack(images), torch.stack(masks), len(images))