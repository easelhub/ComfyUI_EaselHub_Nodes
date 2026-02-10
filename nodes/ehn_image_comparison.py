import os
import numpy as np
from PIL import Image
import folder_paths

class EHN_ImageComparison:
    def __init__(self):
        self.output_dir = folder_paths.get_temp_directory()
        self.type = "temp"
        self.prefix_append = "_EHN_Comp_" + ''.join([str(x) for x in np.random.choice(10, 5)])

    @classmethod
    def INPUT_TYPES(s):
        return {"required": {"image_a": ("IMAGE",), "image_b": ("IMAGE",)}}

    RETURN_TYPES = ()
    FUNCTION = "execute"
    OUTPUT_NODE = True
    CATEGORY = "EaselHub Nodes/Image"

    def execute(self, image_a, image_b):
        results = []
        for i, (img, suffix) in enumerate([(image_a[0], "a"), (image_b[0], "b")]):
            img_pil = Image.fromarray(np.clip(255. * img.cpu().numpy(), 0, 255).astype(np.uint8))
            filename = f"{self.prefix_append}_{suffix}_{i}.png"
            img_pil.save(os.path.join(self.output_dir, filename))
            results.append({"filename": filename, "subfolder": "", "type": self.type})
        return {"ui": {"ehn_comparison_images": results}}