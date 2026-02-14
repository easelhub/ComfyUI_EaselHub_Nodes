from nodes import PreviewImage

class Easel_ImageComparer(PreviewImage):
    CATEGORY, RETURN_TYPES, FUNCTION, OUTPUT_NODE = "EaselHub/Image", (), "compare", True
    @classmethod
    def INPUT_TYPES(s): return {"required": {}, "optional": {"image_a": ("IMAGE",), "image_b": ("IMAGE",)}, "hidden": {"prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO"}}
    def compare(self, image_a=None, image_b=None, filename_prefix="easel.compare", prompt=None, extra_pnginfo=None):
        res = {"ui": {"a_images": [], "b_images": []}}
        if image_a is not None and len(image_a) > 0: res['ui']['a_images'] = self.save_images(image_a, filename_prefix, prompt, extra_pnginfo)['ui']['images']
        if image_b is not None and len(image_b) > 0: res['ui']['b_images'] = self.save_images(image_b, filename_prefix, prompt, extra_pnginfo)['ui']['images']
        return res
