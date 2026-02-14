import torch

class EHN_ColorMatch:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "reference": ("IMAGE",),
                "image": ("IMAGE",),
                "factor": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "execute"
    CATEGORY = "EaselHub/Image"

    def execute(self, reference, image, factor):
        if factor == 0:
            return (image,)

        t_image = image.permute(0, 3, 1, 2)
        t_ref = reference.permute(0, 3, 1, 2)

        if t_image.shape[1] != 3 or t_ref.shape[1] != 3:
            return (image,)

        def rgb2lab(t):
            mask = t > 0.04045
            t = torch.where(mask, ((t + 0.055) / 1.055) ** 2.4, t / 12.92)
            
            r, g, b = t[:, 0, ...], t[:, 1, ...], t[:, 2, ...]
            
            x = 0.4124564 * r + 0.3575761 * g + 0.1804375 * b
            y = 0.2126729 * r + 0.7151522 * g + 0.0721750 * b
            z = 0.0193339 * r + 0.1191920 * g + 0.9503041 * b
            
            xyz = torch.stack((x, y, z), dim=1)
            xyz = xyz / torch.tensor([0.95047, 1.00000, 1.08883], device=xyz.device, dtype=xyz.dtype).view(1, 3, 1, 1)
            
            mask = xyz > 0.008856
            xyz = torch.where(mask, xyz ** (1/3), 7.787 * xyz + 16/116)
            
            l = 116 * xyz[:, 1, ...] - 16
            a = 500 * (xyz[:, 0, ...] - xyz[:, 1, ...])
            b = 200 * (xyz[:, 1, ...] - xyz[:, 2, ...])
            
            return torch.stack((l, a, b), dim=1)

        def lab2rgb(t):
            l, a, b = t[:, 0, ...], t[:, 1, ...], t[:, 2, ...]
            
            y = (l + 16) / 116
            x = a / 500 + y
            z = y - b / 200
            
            xyz = torch.stack((x, y, z), dim=1)
            
            mask = xyz > 0.2068966
            xyz = torch.where(mask, xyz ** 3, (xyz - 16/116) / 7.787)
            
            xyz = xyz * torch.tensor([0.95047, 1.00000, 1.08883], device=xyz.device, dtype=xyz.dtype).view(1, 3, 1, 1)
            
            x, y, z = xyz[:, 0, ...], xyz[:, 1, ...], xyz[:, 2, ...]
            
            r = 3.2404542 * x - 1.5371385 * y - 0.4985314 * z
            g = -0.9692660 * x + 1.8760108 * y + 0.0415560 * z
            b = 0.0556434 * x - 0.2040259 * y + 1.0572252 * z
            
            rgb = torch.stack((r, g, b), dim=1)
            
            mask = rgb > 0.0031308
            rgb = torch.where(mask, 1.055 * (rgb ** (1/2.4)) - 0.055, 12.92 * rgb)
            
            return torch.clamp(rgb, 0, 1)

        lab_image = rgb2lab(t_image)
        lab_ref = rgb2lab(t_ref)

        mean_image = torch.mean(lab_image, dim=(2, 3), keepdim=True)
        std_image = torch.std(lab_image, dim=(2, 3), keepdim=True)
        mean_ref = torch.mean(lab_ref, dim=(2, 3), keepdim=True)
        std_ref = torch.std(lab_ref, dim=(2, 3), keepdim=True)

        l_chan = (lab_image[:, 0:1, ...] - mean_image[:, 0:1, ...]) * (std_ref[:, 0:1, ...] / (std_image[:, 0:1, ...] + 1e-5)) + mean_ref[:, 0:1, ...]
        a_chan = (lab_image[:, 1:2, ...] - mean_image[:, 1:2, ...]) * (std_ref[:, 1:2, ...] / (std_image[:, 1:2, ...] + 1e-5)) + mean_ref[:, 1:2, ...]
        b_chan = (lab_image[:, 2:3, ...] - mean_image[:, 2:3, ...]) * (std_ref[:, 2:3, ...] / (std_image[:, 2:3, ...] + 1e-5)) + mean_ref[:, 2:3, ...]

        result_lab = torch.cat((l_chan, a_chan, b_chan), dim=1)
        result_rgb = lab2rgb(result_lab)
        
        result_rgb = result_rgb.permute(0, 2, 3, 1)
        
        if factor < 1.0:
            result_rgb = image * (1.0 - factor) + result_rgb * factor
            
        return (result_rgb,)
