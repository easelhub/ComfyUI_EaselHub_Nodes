import torch
import torch.nn.functional as F

class Easel_ColorMatch:
    CATEGORY, RETURN_TYPES, RETURN_NAMES, FUNCTION = "EaselHub/Image", ("IMAGE",), ("IMAGE",), "execute"
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {"image": ("IMAGE",), "reference": ("IMAGE",), "method": (["mkl", "hm", "reinhard", "mv", "mvgd", "hm-mvgd"],)}}
    
    def rgb2lab(self, image):
        r, g, b = image[..., 0], image[..., 1], image[..., 2]
        r = torch.where(r > 0.04045, ((r + 0.055) / 1.055) ** 2.4, r / 12.92)
        g = torch.where(g > 0.04045, ((g + 0.055) / 1.055) ** 2.4, g / 12.92)
        b = torch.where(b > 0.04045, ((b + 0.055) / 1.055) ** 2.4, b / 12.92)
        x = r * 0.4124 + g * 0.3576 + b * 0.1805
        y = r * 0.2126 + g * 0.7152 + b * 0.0722
        z = r * 0.0193 + g * 0.1192 + b * 0.9505
        x, y, z = x / 0.95047, y / 1.00000, z / 1.08883
        x = torch.where(x > 0.008856, x ** (1/3), 7.787 * x + 16/116)
        y = torch.where(y > 0.008856, y ** (1/3), 7.787 * y + 16/116)
        z = torch.where(z > 0.008856, z ** (1/3), 7.787 * z + 16/116)
        return torch.stack([116 * y - 16, 500 * (x - y), 200 * (y - z)], dim=-1)

    def lab2rgb(self, image):
        l, a, b = image[..., 0], image[..., 1], image[..., 2]
        y = (l + 16) / 116
        x = a / 500 + y
        z = y - b / 200
        x = torch.where(x ** 3 > 0.008856, x ** 3, (x - 16/116) / 7.787)
        y = torch.where(y ** 3 > 0.008856, y ** 3, (y - 16/116) / 7.787)
        z = torch.where(z ** 3 > 0.008856, z ** 3, (z - 16/116) / 7.787)
        x, y, z = x * 0.95047, y * 1.00000, z * 1.08883
        r = x * 3.2406 + y * -1.5372 + z * -0.4986
        g = x * -0.9689 + y * 1.8758 + z * 0.0415
        b = x * 0.0557 + y * -0.2040 + z * 1.0570
        r = torch.where(r > 0.0031308, 1.055 * (r ** (1/2.4)) - 0.055, 12.92 * r)
        g = torch.where(g > 0.0031308, 1.055 * (g ** (1/2.4)) - 0.055, 12.92 * g)
        b = torch.where(b > 0.0031308, 1.055 * (b ** (1/2.4)) - 0.055, 12.92 * b)
        return torch.stack([r, g, b], dim=-1)

    def execute(self, image, reference, method):
        if image.shape[0] == 0 or reference.shape[0] == 0: return (image,)
        res = []
        for i in range(image.shape[0]):
            img = image[i]
            ref = reference[i % reference.shape[0]]
            img_lab = self.rgb2lab(img)
            ref_lab = self.rgb2lab(ref)
            if method == "reinhard":
                img_mean, img_std = torch.mean(img_lab, dim=(0, 1)), torch.std(img_lab, dim=(0, 1))
                ref_mean, ref_std = torch.mean(ref_lab, dim=(0, 1)), torch.std(ref_lab, dim=(0, 1))
                res_lab = (img_lab - img_mean) * (ref_std / (img_std + 1e-6)) + ref_mean
                res.append(self.lab2rgb(res_lab))
            elif method == "hm":
                res_lab = torch.zeros_like(img_lab)
                for c in range(3):
                    src_flat = img_lab[..., c].view(-1)
                    ref_flat = ref_lab[..., c].view(-1)
                    src_val, src_idx = src_flat.sort()
                    ref_val, _ = ref_flat.sort()
                    if len(ref_val) != len(src_val):
                        ref_val = F.interpolate(ref_val.view(1, 1, -1), size=len(src_val), mode='linear', align_corners=True).view(-1)
                    src_idx_inv = torch.argsort(src_idx)
                    res_lab[..., c] = torch.gather(ref_val, 0, src_idx_inv).view(img_lab.shape[:2])
                res.append(self.lab2rgb(res_lab))
            else:
                img_mean, img_std = torch.mean(img_lab, dim=(0, 1)), torch.std(img_lab, dim=(0, 1))
                ref_mean, ref_std = torch.mean(ref_lab, dim=(0, 1)), torch.std(ref_lab, dim=(0, 1))
                res_lab = (img_lab - img_mean) * (ref_std / (img_std + 1e-6)) + ref_mean
                res.append(self.lab2rgb(res_lab))
        return (torch.stack(res).clamp(0, 1),)
