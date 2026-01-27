import torch

class BaseRes:
    RETURN_TYPES = ("LATENT", "INT", "INT")
    RETURN_NAMES = ("latent", "width", "height")
    FUNCTION = "execute"
    CATEGORY = "EaselHub/Utils"
    _presets = []
    _length = 0

    @classmethod
    def INPUT_TYPES(s):
        inputs = {"required": {"preset": (s._presets,), "batch_size": ("INT", {"default": 1, "min": 1, "max": 64})}}
        if s._length > 0: inputs["required"]["length"] = ("INT", {"default": s._length, "min": 1, "max": 1000})
        return inputs

    def execute(self, preset, batch_size, length=0):
        try:
            dims = preset.split(" ")[0].split("x")
            width, height = int(dims[0]), int(dims[1])
        except:
            width, height = 1024, 1024
        
        latent = self.get_latent(width, height, batch_size, length)
        return ({"samples": latent}, width, height)

    def get_latent(self, w, h, b, l):
        return torch.zeros([b, 4, h // 8, w // 8])

class EHN_FluxResolutions(BaseRes):
    _presets = ["1024x1024 (1:1 Square) 1.0MP","896x1152 (4:5 Portrait) 1.0MP","1152x896 (5:4 Landscape) 1.0MP","832x1216 (2:3 Portrait) 1.0MP","1216x832 (3:2 Landscape) 1.0MP","768x1344 (9:16 Portrait) 1.0MP","1344x768 (16:9 Landscape) 1.0MP","640x1536 (1:2.4 Portrait) 1.0MP","1536x640 (2.4:1 Landscape) 1.0MP","2048x1143 (~16:9 Docs Example) 2.3MP","1920x1440 (4:3 Docs Example) 2.7MP","720x1456 (Docs Example) 1.0MP","1440x1440 (1:1 Square) 2.0MP","1088x1920 (9:16 HD) 2.0MP","1920x1088 (16:9 HD) 2.0MP"]

class EHN_QwenImageResolutions(BaseRes):
    _presets = ["1328x1328 (1:1)","1664x928 (16:9)","928x1664 (9:16)","1472x1104 (4:3)","1104x1472 (3:4)","1584x1056 (3:2)","1056x1584 (2:3)"]

class EHN_ZImageResolutions(BaseRes):
    _presets = ["1024x1024 (1:1)","1152x896 (9:7)","896x1152 (7:9)","1152x864 (4:3)","864x1152 (3:4)","1248x832 (3:2)","832x1248 (2:3)","1280x720 (16:9)","720x1280 (9:16)","1344x576 (21:9)","576x1344 (9:21)","1280x1280 (1:1)","1440x1120 (9:7)","1120x1440 (7:9)","1472x1104 (4:3)","1104x1472 (3:4)","1536x1024 (3:2)","1024x1536 (2:3)","1536x864 (16:9)","864x1536 (9:16)","1680x720 (21:9)","720x1680 (9:21)","1536x1536 (1:1)","1728x1344 (9:7)","1344x1728 (7:9)","1728x1296 (4:3)","1296x1728 (3:4)","1872x1248 (3:2)","1248x1872 (2:3)","2048x1152 (16:9)","1152x2048 (9:16)","2016x864 (21:9)","864x2016 (9:21)"]

class EHN_LTXResolutions(BaseRes):
    _presets = ["1216x704 (Default) 0.9MP","704x1216 (Default Portrait) 0.9MP","768x512 (Standard) 0.4MP","512x768 (Standard Portrait) 0.4MP","1024x576 (16:9) 0.6MP","576x1024 (9:16) 0.6MP","1280x720 (720p) 0.9MP","720x1280 (720p Portrait) 0.9MP","1920x1080 (1080p) 2.1MP","1080x1920 (1080p Portrait) 2.1MP","3840x2160 (4K) 8.3MP"]
    _length = 121
    def get_latent(self, w, h, b, l): return torch.zeros([b, 4, l, h // 8, w // 8])

class EHN_WanResolutions(BaseRes):
    _presets = ["1280x720 (720p Landscape) Wan2.1","720x1280 (720p Portrait) Wan2.1","832x480 (480p Landscape) Wan2.1","480x832 (480p Portrait) Wan2.1","1280x704 (720p Landscape) Wan2.2","704x1280 (720p Portrait) Wan2.2","1024x1024 (Square) Image"]
    _length = 81
    def get_latent(self, w, h, b, l): return torch.zeros([b, 4, l, h // 8, w // 8])

class EHN_HiDreamResolutions(BaseRes):
    _presets = ["1024x1024 (Square)"]

class EHN_HunyuanResolutions(BaseRes):
    _presets = ["1280x720 (720p Landscape)","720x1280 (720p Portrait)","960x544 (540p Landscape)","544x960 (540p Portrait)","1280x960 (4:3 Landscape)","960x1280 (3:4 Portrait)","1104x832 (4:3 Landscape)","832x1104 (3:4 Portrait)","832x624 (4:3 Landscape)","624x832 (3:4 Portrait)","960x960 (Square)","720x720 (Square)"]
    _length = 129
    def get_latent(self, w, h, b, l): return torch.zeros([b, 16, l // 4, h // 8, w // 8])


