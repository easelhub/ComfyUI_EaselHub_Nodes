import torch

class EHN_ColorMatch:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "reference": ("IMAGE",),
                "method": (["mkl", "hm", "reinhard", "mv", "mvgd", "hm-mvgd"],),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "execute"
    CATEGORY = "EaselHub/Image"

    def execute(self, image, reference, method):
        if image.shape[0] == 0 or reference.shape[0] == 0:
            return (image,)

        t_image = image.permute(0, 3, 1, 2)
        t_ref = reference.permute(0, 3, 1, 2)

        if t_ref.shape[2:] != t_image.shape[2:]:
            t_ref = torch.nn.functional.interpolate(t_ref, size=t_image.shape[2:], mode="bicubic", align_corners=False)

        def get_mean_std(img):
            mean = torch.mean(img, dim=(2, 3), keepdim=True)
            std = torch.std(img, dim=(2, 3), keepdim=True)
            return mean, std

        def reinhard(src, ref):
            src_mean, src_std = get_mean_std(src)
            ref_mean, ref_std = get_mean_std(ref)
            return (src - src_mean) * (ref_std / (src_std + 1e-6)) + ref_mean

        def hist_match(src, ref):
            b, c, h, w = src.shape
            src_flat = src.view(b, c, -1)
            ref_flat = ref.view(b, c, -1)
            
            src_val, src_idx = src_flat.sort(dim=-1)
            ref_val, _ = ref_flat.sort(dim=-1)
            
            src_idx_inv = torch.argsort(src_idx, dim=-1)
            out_flat = torch.gather(ref_val, -1, src_idx_inv)
            return out_flat.view(b, c, h, w)

        if method == "reinhard":
            res = reinhard(t_image, t_ref)
        elif method == "hm":
            res = hist_match(t_image, t_ref)
        elif method == "mkl":
            src_mean = torch.mean(t_image, dim=(2, 3), keepdim=True)
            ref_mean = torch.mean(t_ref, dim=(2, 3), keepdim=True)
            
            src_centered = (t_image - src_mean).flatten(2)
            ref_centered = (t_ref - ref_mean).flatten(2)
            
            cov_src = torch.matmul(src_centered, src_centered.transpose(1, 2)) / (src_centered.shape[2] - 1)
            cov_ref = torch.matmul(ref_centered, ref_centered.transpose(1, 2)) / (ref_centered.shape[2] - 1)
            
            # Add epsilon for stability
            cov_src += torch.eye(3, device=cov_src.device) * 1e-6
            cov_ref += torch.eye(3, device=cov_ref.device) * 1e-6

            u, s, v = torch.svd(cov_src)
            cov_src_sqrt = torch.matmul(u, torch.matmul(torch.diag_embed(s.sqrt()), v.transpose(1, 2)))
            cov_src_inv_sqrt = torch.matmul(u, torch.matmul(torch.diag_embed(1 / s.sqrt()), v.transpose(1, 2)))
            
            term = torch.matmul(torch.matmul(cov_src_sqrt, cov_ref), cov_src_sqrt)
            u2, s2, v2 = torch.svd(term)
            term_sqrt = torch.matmul(u2, torch.matmul(torch.diag_embed(s2.sqrt()), v2.transpose(1, 2)))
            
            t_mat = torch.matmul(torch.matmul(cov_src_inv_sqrt, term_sqrt), cov_src_inv_sqrt)
            
            res = torch.matmul(t_mat, src_centered).view(t_image.shape[0], 3, t_image.shape[2], t_image.shape[3]) + ref_mean
            
        elif method == "mv":
            res = reinhard(t_image, t_ref)
            
        elif method == "mvgd":
             res = reinhard(t_image, t_ref)
             
        elif method == "hm-mvgd":
             res = hist_match(reinhard(t_image, t_ref), t_ref)
             
        else:
            res = t_image

        return (torch.clamp(res.permute(0, 2, 3, 1), 0, 1),)
