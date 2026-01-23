import torch

class EHN_SmartResolution:
    """
    EaselHub Smart Resolution Calculator
    Calculates optimal latent dimensions based on model architecture and target aspect ratio.
    """
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "model_version": ([
                    "Flux.1 / SD 3.5 (64px)", 
                    "SDXL / Pony (32px)",
                    "Wan 2.1 / Hunyuan Video (16px)",
                    "CogVideoX / Mochi (32px)",
                    "Hunyuan DiT / Kolors (32px)",
                    "Sana / PixArt / Lumina (32px)",
                    "Stable Cascade / SVD (64px)",
                    "Z-Image / Qwen-VL (16px)",
                    "SD 1.5 / Legacy (8px)",
                    "DeepFloyd IF (64px)"
                ],),
                
                "calc_mode": ([
                    "Fix Width (Calculate Height)", 
                    "Fix Height (Calculate Width)"
                ],),
                
                "base_length": ("INT", {
                    "default": 1024, 
                    "min": 256, 
                    "max": 16384, 
                    "step": 32, 
                    "display": "number"
                }),
                
                "aspect_ratio": ([
                    "1:1 Square",
                    "16:9 Landscape",
                    "9:16 Portrait",
                    "4:3 Photo Landscape",
                    "3:4 Photo Portrait",
                    "3:2 Classic Landscape",
                    "2:3 Classic Portrait",
                    "21:9 Cinema",
                    "9:21 Mobile Ultra",
                    "2:1 Wide",
                    "1:2 Tall",
                    "1.85:1 Cinema Std",
                    "2.39:1 Anamorphic"
                ],),
                
                "batch_size": ("INT", {"default": 1, "min": 1, "max": 64}),
            },
            # Hidden input to store frontend state if needed in future
            "hidden": {
                "ui_info": ("STRING", {"default": ""}),
            }
        }

    RETURN_TYPES = ("LATENT", "INT", "INT", "STRING")
    RETURN_NAMES = ("Latent", "Width", "Height", "Info")
    FUNCTION = "execute_calculation"
    CATEGORY = "EaselHub/Utils"

    def execute_calculation(self, model_version, calc_mode, base_length, aspect_ratio, batch_size, ui_info=None):
        # 1. Determine Alignment Factor (Stride)
        align_factor = 8
        model_map = {
            "Flux": 64, "SD 3.5": 64, "Cascade": 64, "SVD": 64, "DeepFloyd": 64,
            "SDXL": 32, "Pony": 32, "CogVideoX": 32, "Mochi": 32, "Hunyuan DiT": 32, 
            "Kolors": 32, "Sana": 32, "PixArt": 32,
            "Wan": 16, "Hunyuan Video": 16, "Z-Image": 16, "Qwen": 16
        }
        
        for key, val in model_map.items():
            if key in model_version:
                align_factor = val
                break
        
        # 2. Parse Aspect Ratio
        try:
            ratio_str = aspect_ratio.split(" ")[0]
            w_r, h_r = map(float, ratio_str.split(":"))
            target_ratio = w_r / h_r
        except:
            target_ratio = 1.0  # Fallback
            ratio_str = "1:1"

        # 3. Calculate Dimensions
        final_w = 1024
        final_h = 1024

        if "Width" in calc_mode:
            # Fix Width -> Calc Height
            final_w = (base_length // align_factor) * align_factor
            if final_w == 0: final_w = align_factor
            
            raw_h = final_w / target_ratio
            final_h = round(raw_h / align_factor) * align_factor
            if final_h == 0: final_h = align_factor
        else:
            # Fix Height -> Calc Width
            final_h = (base_length // align_factor) * align_factor
            if final_h == 0: final_h = align_factor
            
            raw_w = final_h * target_ratio
            final_w = round(raw_w / align_factor) * align_factor
            if final_w == 0: final_w = align_factor

        # 4. Create Latent
        # Latents are typically 1/8th of pixel dimensions for SD/Flux
        # Note: Some video models use different latent factors, but Comfy standardizes 
        # the EmptyLatent output to be compatible with the pixel dimensions/8 convention usually.
        # We output standard SD-compatible latent structure.
        latent_h = final_h // 8
        latent_w = final_w // 8
        
        latent_tensor = torch.zeros([batch_size, 4, latent_h, latent_w])
        latent_out = {"samples": latent_tensor}
        
        # 5. Generate Info String
        mp = round((final_w * final_h) / 1000000, 2)
        short_name = model_version.split('(')[0].strip()
        
        info_str = (f"Model: {short_name}\n"
                    f"Size: {final_w}x{final_h}\n"
                    f"Ratio: {ratio_str}\n"
                    f"Pixels: {mp} MP")

        return (latent_out, final_w, final_h, info_str)