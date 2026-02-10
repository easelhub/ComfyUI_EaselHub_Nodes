import torch
import numpy as np
from PIL import Image
import folder_paths
import os
import random

class EHN_ImageCompare:
    def __init__(self):
        self.output_dir = folder_paths.get_temp_directory()
        self.type = "temp"
        self.prefix = "ehn_compare_"

    @classmethod
    def INPUT_TYPES(s):
        return {"required": {"image_a": ("IMAGE",), "image_b": ("IMAGE",)}}
    
    RETURN_TYPES = ()
    FUNCTION = "compare"
    OUTPUT_NODE = True
    CATEGORY = "EaselHub/Image"

    def compare(self, image_a, image_b):
        results = []
        for img in [image_a, image_b]:
            i = 255. * img[0].cpu().numpy()
            img_pil = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
            file = f"{self.prefix}_{random.randint(1, 10000000)}.png"
            img_pil.save(os.path.join(self.output_dir, file))
            results.append({"filename": file, "subfolder": "", "type": self.type})
        return {"ui": {"images": results}}
