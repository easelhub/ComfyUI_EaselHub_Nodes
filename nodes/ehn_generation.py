import torch

class EHN_SmartResolution:
    
    # 2026 Updated Database
    MODEL_DB = {
        "[China] Z-Image / SDXL Optimized": (32, 1024),
        "[China] Hunyuan DiT": (32, 1024),
        "[China] Kolors (Kwai)": (32, 1024),
        "[China] Wan 2.1 (Video)": (16, 720),
        "[China] CogVideoX": (32, 720),
        
        "[8GB] Flux.1 Schnell/NF4": (16, 896),
        "[8GB] PixArt Sigma": (32, 1024),
        "[8GB] SDXL Turbo": (32, 1024),
        "[8GB] Hunyuan Video (Low)": (16, 512),
        
        "[Flux] Flux.1 Dev/Pro": (16, 1024),
        "[SD3] Stable Diffusion 3.5": (16, 1024),
        "[SDXL] Pony V6 / NoobAI": (32, 1024),
        "[SDXL] Base 1.0": (32, 1024),
        "[Video] Hunyuan Video": (16, 720),
        "[Video] LTX-Video": (32, 768),
        "[Video] Mochi 1": (8, 848),
        
        "[Legacy] SD 1.5": (8, 512),
        "[Legacy] SD 2.1": (8, 768),
    }

    @classmethod
    def INPUT_TYPES(s):
        model_list = sorted(list(s.MODEL_DB.keys()))
        return {
            "required": {
                "model_type": (model_list,),
                "calc_mode": ([
                    "Fix Longest Edge", "Fix Shortest Edge",
                    "Fix Width", "Fix Height", "Direct (Ignore Ratio)"
                ],),
                "base_length": ("INT", {"default": 1024, "min": 64, "max": 8192, "step": 16}),
                "aspect_ratio": ([
                    "1:1", "3:4", "4:3", "9:16", "16:9", "2:3", "3:2", "21:9", "9:21",
                    "1280x720 (720p)", "720x1280 (720p V)", "1920x1080 (1080p)", "Custom"
                ],),
                "batch_size": ("INT", {"default": 1, "min": 1, "max": 64}),
            },
        }

    RETURN_TYPES = ("LATENT", "INT", "INT", "STRING")
    RETURN_NAMES = ("EmptyLatent", "Width", "Height", "Info")
    FUNCTION = "execute"
    CATEGORY = "EaselHub/Generation"

    def execute(self, model_type, calc_mode, base_length, aspect_ratio, batch_size):
        spec = self.MODEL_DB.get(model_type, (32, 1024))
        align = spec[0]
        
        w, h = base_length, base_length
        target_ratio = 1.0
        is_fixed = False

        if "x" in aspect_ratio and ":" not in aspect_ratio:
            try:
                dims = aspect_ratio.split(" ")[0].split("x")
                w, h = int(dims[0]), int(dims[1])
                target_ratio = w / h
                is_fixed = True
            except: pass
        elif ":" in aspect_ratio:
            try:
                parts = aspect_ratio.split(" ")[0].split(":")
                target_ratio = float(parts[0]) / float(parts[1])
            except: pass

        def align_val(x): return max(align, (int(x) // align) * align)

        if "Direct" in calc_mode:
            w, h = align_val(base_length), align_val(base_length)
        elif is_fixed:
            w, h = align_val(w), align_val(h)
        else:
            if "Fix Width" in calc_mode:
                w = align_val(base_length); h = align_val(w / target_ratio)
            elif "Fix Height" in calc_mode:
                h = align_val(base_length); w = align_val(h * target_ratio)
            elif "Fix Longest" in calc_mode:
                if target_ratio >= 1: w, h = align_val(base_length), align_val(base_length / target_ratio)
                else: h, w = align_val(base_length), align_val(base_length * target_ratio)
            elif "Fix Shortest" in calc_mode:
                if target_ratio >= 1: h, w = align_val(base_length), align_val(base_length * target_ratio)
                else: w, h = align_val(base_length), align_val(base_length / target_ratio)

        latent = {"samples": torch.zeros([batch_size, 4, h // 8, w // 8])}
        
        mp = (w * h) / 1e6
        short_name = model_type.split("] ")[1] if "]" in model_type else model_type
        info = (f"Model: {short_name}\nRes: {w}x{h} (Align {align})\nMP: {mp:.2f}")

        return (latent, w, h, info)