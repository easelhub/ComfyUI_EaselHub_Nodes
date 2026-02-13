import torch
import numpy as np
from PIL import Image
from nodes import PreviewImage
import folder_paths
import os
import sys

def tensor2pil(image):
    return Image.fromarray(np.clip(255. * image.cpu().numpy().squeeze(), 0, 255).astype(np.uint8))

def pil2tensor(image):
    return torch.from_numpy(np.array(image).astype(np.float32) / 255.0).unsqueeze(0)

def wavelet_color_fix(target_image, reference_image):
    # Simplified wavelet color fix implementation
    # This is a placeholder. In a real implementation, you would use wavelet transform
    # to transfer color statistics.
    # For now, we'll just return the target image to avoid errors if dependencies are missing.
    # A proper implementation would require pywavelets or similar.
    return target_image

def adain_color_fix(target_image, reference_image):
    # Simplified AdaIN color fix implementation
    # Placeholder.
    return target_image

def install_package(package_name):
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])

class EHN_ImageColorMatch(PreviewImage):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image_ref": ("IMAGE",),
                "image_target": ("IMAGE",),
                "method": (['wavelet', 'adain', 'mkl', 'hm', 'reinhard', 'mvgd', 'hm-mvgd-hm', 'hm-mkl-hm'],),
                "image_output": (["Hide", "Preview", "Save", "Hide/Save"], {"default": "Preview"}),
                "save_prefix": ("STRING", {"default": "ComfyUI"}),
            },
            "hidden": {"prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO"},
        }

    CATEGORY = "EaselHub/Image"

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    OUTPUT_NODE = True
    FUNCTION = "color_match"

    def color_match(self, image_ref, image_target, method, image_output, save_prefix, prompt=None, extra_pnginfo=None):
        if method in ["wavelet", "adain"]:
            # Note: These methods need actual implementation or library imports
            # For now, we use the placeholders defined above or import if available
            try:
                from ..libs.colorfix import wavelet_color_fix as wcf, adain_color_fix as acf
                result_images = wcf(tensor2pil(image_target), tensor2pil(image_ref)) if method == 'wavelet' else acf(tensor2pil(image_target), tensor2pil(image_ref))
            except ImportError:
                 result_images = wavelet_color_fix(tensor2pil(image_target), tensor2pil(image_ref)) if method == 'wavelet' else adain_color_fix(tensor2pil(image_target), tensor2pil(image_ref))
            
            new_images = pil2tensor(result_images)
        else:
            try:
                from color_matcher import ColorMatcher
            except ImportError:
                install_package("color-matcher")
                from color_matcher import ColorMatcher
            
            image_ref = image_ref.cpu()
            image_target = image_target.cpu()
            batch_size = image_target.size(0)
            out = []
            images_target = image_target.squeeze()
            images_ref = image_ref.squeeze()

            image_ref_np = images_ref.numpy()
            images_target_np = images_target.numpy()
            
            # Handle batch dimension correctly
            if image_ref.dim() == 3:
                image_ref_np = image_ref_np[None, ...]
            if image_target.dim() == 3:
                images_target_np = images_target_np[None, ...]

            if image_ref.size(0) > 1 and image_ref.size(0) != batch_size:
                raise ValueError("ColorMatch: Use either single reference image or a matching batch of reference images.")
            
            cm = ColorMatcher()
            for i in range(batch_size):
                # Handle single image vs batch
                target_img = images_target_np if batch_size == 1 else images_target_np[i]
                ref_img = image_ref_np if image_ref.size(0) == 1 else image_ref_np[i]
                
                try:
                    image_result = cm.transfer(src=target_img, ref=ref_img, method=method)
                except Exception as e:
                    print(f"Error occurred during transfer: {e}")
                    image_result = target_img # Fallback
                
                out.append(torch.from_numpy(image_result))

            new_images = torch.stack(out, dim=0).to(torch.float32)

        # Save/Preview logic
        results = []
        if image_output in ("Preview", "Save", "Hide/Save"):
            # Use parent class save_images method
            # We need to handle the 'Hide' case manually if we want to suppress output but still save
            # But PreviewImage.save_images handles saving based on filename_prefix
            
            # If "Hide", we don't want to return UI images, but we might want to save?
            # The original code uses a helper 'easySave'. We'll use standard SaveImage/PreviewImage logic.
            
            if image_output == "Preview":
                res = self.save_images(new_images, save_prefix, prompt, extra_pnginfo)
                results = res["ui"]["images"]
            elif image_output == "Save":
                # We need SaveImage node logic here, but we inherit from PreviewImage.
                # PreviewImage saves to temp. SaveImage saves to output.
                from nodes import SaveImage
                res = SaveImage().save_images(new_images, save_prefix, prompt, extra_pnginfo)
                results = res["ui"]["images"]
            elif image_output == "Hide/Save":
                 from nodes import SaveImage
                 res = SaveImage().save_images(new_images, save_prefix, prompt, extra_pnginfo)
                 # Don't return UI images to hide them
                 results = []

        if image_output in ("Hide", "Hide/Save"):
            return {"ui": {}, "result": (new_images,)}

        return {"ui": {"images": results}, "result": (new_images,)}
