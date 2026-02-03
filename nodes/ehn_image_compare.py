import os, random
import numpy as np
from PIL import Image
import folder_paths

class EHN_ImageCompare:
    def __init__(self):
        self.output_dir = folder_paths.get_temp_directory()
        self.type = 'temp'
        self.prefix = f'_temp_{random.randint(10000, 99999)}_'

    @classmethod
    def INPUT_TYPES(s):
        return {'required': {'image_a': ('IMAGE',), 'image_b': ('IMAGE',)}}

    RETURN_TYPES = ()
    FUNCTION = 'compare'
    OUTPUT_NODE = True
    CATEGORY = 'EaselHub/Image'
    DESCRIPTION = "Side-by-side comparison of two images in the UI."

    def compare(self, image_a, image_b):
        res = []
        def save(t, s):
            i = Image.fromarray(np.clip(255. * t.cpu().numpy(), 0, 255).astype(np.uint8))
            fn = f'cmp_{s}_{self.prefix}_{random.randint(1,100000)}.png'
            i.save(os.path.join(self.output_dir, fn))
            return {'filename': fn, 'subfolder': '', 'type': self.type}
        
        if image_a is not None and len(image_a): res.append(save(image_a[0], 'a'))
        if image_b is not None and len(image_b): res.append(save(image_b[0], 'b'))
        return {'ui': {'comparison_images': res}}
