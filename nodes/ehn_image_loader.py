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
                "image_limit": ("INT", {"default": 99, "min": 1, "max": 10000}),
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
        if not os.path.isdir(directory):
            raise FileNotFoundError(f"Directory not found: {directory}")

        file_paths = []
        valid_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff', '.gif'}

        if recursive:
            for root, _, files in os.walk(directory):
                for file in files:
                    if os.path.splitext(file)[1].lower() in valid_extensions:
                        file_paths.append(os.path.join(root, file))
        else:
            for file in os.listdir(directory):
                if os.path.splitext(file)[1].lower() in valid_extensions:
                    file_paths.append(os.path.join(directory, file))

        if sort_method == "filename_asc":
            file_paths.sort()
        elif sort_method == "filename_desc":
            file_paths.sort(reverse=True)
        elif sort_method == "random":
            random.shuffle(file_paths)

        total_images = len(file_paths)
        if start_index >= total_images:
            return (torch.zeros((1, 64, 64, 3)), torch.zeros((1, 64, 64)), 0)

        end_index = start_index + image_limit
        selected_files = file_paths[start_index:end_index]

        images = []
        masks = []
        
        first_width = 0
        first_height = 0

        for file_path in selected_files:
            try:
                img = Image.open(file_path)
                img = ImageOps.exif_transpose(img)
                
                if img.mode == 'I':
                    img = img.point(lambda i: i * (1 / 255))
                
                if 'A' in img.getbands():
                    mask = np.array(img.getchannel('A')).astype(np.float32) / 255.0
                    mask = 1. - mask
                else:
                    mask = np.zeros((img.height, img.width), dtype=np.float32)

                img = img.convert("RGB")
                
                if len(images) == 0:
                    first_width, first_height = img.size
                else:
                    if img.size != (first_width, first_height):
                        img = img.resize((first_width, first_height), Image.BILINEAR)
                        if isinstance(mask, np.ndarray):
                            mask = torch.from_numpy(mask)
                        if mask.dim() == 2:
                            mask = mask.unsqueeze(0).unsqueeze(0)
                        mask = torch.nn.functional.interpolate(
                            mask,
                            size=(first_height, first_width),
                            mode="bilinear",
                            align_corners=False
                        ).squeeze()

                image = torch.from_numpy(np.array(img)).float() / 255.0
                image = image.unsqueeze(0)
                
                if isinstance(mask, np.ndarray):
                    mask = torch.from_numpy(mask)
                if mask.dim() == 2:
                    mask = mask.unsqueeze(0)
                
                images.append(image)
                masks.append(mask)
                
            except Exception:
                continue

        if not images:
            return (torch.zeros((1, 64, 64, 3)), torch.zeros((1, 64, 64)), 0)

        return (torch.cat(images, dim=0), torch.cat(masks, dim=0), len(images))
