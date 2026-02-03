import torch, torch.nn.functional as F
from .ehn_utils import fill_mask_holes

class EHN_ImageStack:
    INPUT_IS_LIST = True
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image_1": ("IMAGE",),
                "layout_mode": (["Horizontal", "Vertical", "Grid"], {"default": "Horizontal"}),
                "max_columns": ("INT", {"default": 2}),
                "resize_behavior": (["None", "Resize to First", "Fixed Width", "Fixed Height"], {"default": "None"}),
                "resize_value": ("INT", {"default": 1024}),
                "alignment": (["Top Left", "Center", "Bottom Right"], {"default": "Center"}),
                "gap": ("INT", {"default": 0}), "border_width": ("INT", {"default": 0}),
                "fill_color": ("STRING", {"default": "#FFFFFF"}),
                "mask_blur": ("INT", {"default": 0}),
                "fill_holes": ("BOOLEAN", {"default": False}),
            },
            "optional": { "mask_1": ("MASK",) }
        }
    RETURN_TYPES = ("IMAGE", "MASK", "INT", "INT")
    RETURN_NAMES = ("Image", "Mask", "Width", "Height")
    FUNCTION = "execute_stack"
    CATEGORY = "EaselHub/Image"
    DESCRIPTION = "Stacks multiple images into a grid, strip, or column with alignment and resizing options."

    def execute_stack(self, image_1, layout_mode, max_columns, resize_behavior, resize_value, alignment, gap, border_width, fill_color, fill_holes, mask_blur, mask_1=None, **kwargs):
        up = lambda x: x[0] if isinstance(x, list) and x else x
        layout, max_c, r_behav, r_val, align, gp, bw, fc, fh, mb = map(up, [layout_mode, max_columns, resize_behavior, resize_value, alignment, gap, border_width, fill_color, fill_holes, mask_blur])
        
        # Normalize inputs
        layout = layout.lower()
        r_behav = r_behav.lower().replace(" ", "_")
        align = align.lower().replace(" ", "_")

        all_ins = {"image_1": image_1, "mask_1": mask_1, **kwargs}
        keys = sorted([k for k in all_ins if k.startswith("image_")], key=lambda x: int(x.split("_")[1]))
        
        imgs_flat, msks_flat = [], []
        for k in keys:
            ilist = all_ins[k]
            mlist = all_ins.get(f"mask_{k.split('_')[-1]}", [None]*len(ilist))
            for i, img in enumerate(ilist):
                for b in range(img.shape[0]):
                    imgs_flat.append(img[b])
                    m = mlist[i][b] if mlist[i] is not None else torch.ones(img.shape[:2], device=img.device)
                    msks_flat.append(m)

        if not imgs_flat: return (torch.zeros((1,512,512,3)), torch.zeros((1,512,512)), 512, 512)

        p_imgs, p_msks = [], []
        th, tw = 0, 0
        if r_behav == "resize_to_first": th, tw = imgs_flat[0].shape[:2]
        elif r_behav == "fixed_width": tw = r_val
        elif r_behav == "fixed_height": th = r_val

        for img, msk in zip(imgs_flat, msks_flat):
            h, w = img.shape[:2]
            if msk.shape != (h, w): msk = F.interpolate(msk[None, None], size=(h, w), mode='nearest')[0, 0]
            nh, nw, resize = h, w, False
            if r_behav != "none":
                if r_behav == "fixed_width" and w != tw: resize, nw, nh = True, tw, int(h * (tw/w))
                elif r_behav == "fixed_height" and h != th: resize, nh, nw = True, th, int(w * (th/h))
                elif r_behav == "resize_to_first" and (w, h) != (tw, th):
                    resize, s = True, max(tw/w, th/h)
                    nw, nh = int(w*s), int(h*s)

            if resize:
                img = F.interpolate(img.permute(2,0,1)[None], size=(nh, nw), mode='bicubic')[0].permute(1,2,0)
                msk = F.interpolate(msk[None, None], size=(nh, nw), mode='bilinear')[0, 0]
                if r_behav == "resize_to_first":
                    cx, cy = (nw-tw)//2, (nh-th)//2
                    img, msk = img[cy:cy+th, cx:cx+tw], msk[cy:cy+th, cx:cx+tw]
            p_imgs.append(img); p_msks.append(msk)

        rows = []
        if layout == "horizontal": rows = [p_imgs]
        elif layout == "vertical": rows = [[i] for i in p_imgs]
        else:
            for i in range(0, len(p_imgs), max_c): rows.append(p_imgs[i:i+max_c])
        
        row_dims = [(max(i.shape[0] for i in r), sum(i.shape[1] for i in r) + gp * (len(r) - 1)) for r in rows if r]
        if not row_dims: return (torch.zeros((1,512,512,3)), torch.zeros((1,512,512)), 512, 512)

        total_h = sum(h for h, _ in row_dims) + gp * (len(rows) - 1) + 2 * bw
        total_w = max(w for _, w in row_dims) + 2 * bw
        
        try: bg = tuple(int(fc.lstrip("#")[i:i+2], 16)/255. for i in (0,2,4))
        except: bg = (1.,1.,1.)
        
        cv = torch.tensor(bg, device=p_imgs[0].device).view(1,1,3).repeat(total_h, total_w, 1)
        mk = torch.zeros((total_h, total_w), device=p_imgs[0].device)
        
        cy = bw
        idx = 0
        for r_idx, r_imgs in enumerate(rows):
            rh, rw = row_dims[r_idx]
            cx = bw
            if align == "center": cx += (total_w - 2*bw - rw)//2
            elif align == "bottom_right": cx += (total_w - 2*bw - rw)
            
            for i_idx, img in enumerate(r_imgs):
                h, w = img.shape[:2]
                y_off = (rh - h)//2 if align == "center" else (rh - h if align == "bottom_right" else 0)
                py, px = cy + y_off, cx
                cv[py:py+h, px:px+w] = img
                mk[py:py+h, px:px+w] = p_msks[idx]
                cx += w + gp
                idx += 1
            cy += rh + gp

        if fh:
             mk = fill_mask_holes(mk)

        if mb > 0:
            mk = F.avg_pool2d(F.pad(mk[None, None], [mb]*4, mode='reflect'), mb*2+1, 1)[0, 0]

        return (cv.unsqueeze(0), mk.unsqueeze(0), total_w, total_h)