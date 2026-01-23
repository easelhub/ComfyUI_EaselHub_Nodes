import torch
import torch.nn.functional as F

class EHN_ImageResize:
    """
    高级图像缩放节点 (EHN Image Resize)
    修复了 'permutedim' 属性错误，使用正确的 .permute() 方法。
    """
    
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "width": ("INT", {"default": 512, "min": 0, "max": 16384, "step": 1}),
                "height": ("INT", {"default": 512, "min": 0, "max": 16384, "step": 1}),
                "interpolation": (["nearest", "bilinear", "bicubic", "area", "lanczos"], {"default": "nearest"}),
                "method": (["stretch", "keep proportion", "fill / crop", "pad (letterbox)"], {"default": "stretch"}),
                "condition": (["always", "downscale only", "upscale only", "if input is larger", "if input is smaller"], {"default": "always"}),
                "multiple_of": ("INT", {"default": 0, "min": 0, "max": 512, "step": 1}),
            },
            "optional": {
                "mask": ("MASK",),
            }
        }

    RETURN_TYPES = ("IMAGE", "MASK", "INT", "INT")
    RETURN_NAMES = ("IMAGE", "MASK", "width", "height")
    FUNCTION = "execute"
    CATEGORY = "EaselHub/Image"

    def execute(self, image, width, height, interpolation, method, condition, multiple_of, mask=None):
        # 1. 获取输入尺寸 (Batch, Height, Width, Channel)
        _, h, w, _ = image.shape
        
        # 2. 目标尺寸计算逻辑
        if width == 0 and height == 0:
            target_w, target_h = w, h
        elif width == 0:
            target_w = int(w * (height / h))
            target_h = height
        elif height == 0:
            target_w = width
            target_h = int(h * (width / w))
        else:
            target_w, target_h = width, height

        # 3. Method 逻辑
        if method == "keep proportion":
            scale = min(target_w / w, target_h / h)
            target_w = int(w * scale)
            target_h = int(h * scale)
        elif method == "fill / crop":
            scale = max(target_w / w, target_h / h)
            resize_w = int(w * scale)
            resize_h = int(h * scale)
        elif method == "pad (letterbox)":
            scale = min(target_w / w, target_h / h)
            resize_w = int(w * scale)
            resize_h = int(h * scale)
        else: # stretch
            resize_w, resize_h = target_w, target_h

        if method not in ["fill / crop", "pad (letterbox)"]:
            resize_w, resize_h = target_w, target_h

        # 4. Multiple of
        if multiple_of > 1:
            resize_w = (resize_w // multiple_of) * multiple_of
            resize_h = (resize_h // multiple_of) * multiple_of
            if method == "stretch":
                target_w, target_h = resize_w, resize_h

        # 5. Condition check
        should_resize = False
        if condition == "always":
            should_resize = True
        elif condition == "downscale only":
            if resize_w < w or resize_h < h: should_resize = True
        elif condition == "upscale only":
            if resize_w > w or resize_h > h: should_resize = True
        elif condition == "if input is larger":
            if w > target_w or h > target_h: should_resize = True
        elif condition == "if input is smaller":
            if w < target_w or h < target_h: should_resize = True

        if not should_resize:
            out_mask = mask if mask is not None else torch.zeros((1, h, w), device=image.device, dtype=torch.float32)
            return (image, out_mask, w, h)

        # 6. 执行缩放 (Image)
        # 错误修复：使用 .permute() 而不是 .permutedim()
        img_permuted = image.permute(0, 3, 1, 2)
        
        def do_resize(tensor_bchw, rw, rh, mode):
            return F.interpolate(tensor_bchw, size=(rh, rw), mode=mode)

        resized_img = do_resize(img_permuted, resize_w, resize_h, interpolation)

        # 7. 执行缩放 (Mask)
        resized_mask = None
        if mask is not None:
            if mask.dim() == 2:
                mask = mask.unsqueeze(0)
            mask_expanded = mask.unsqueeze(1) # (B, 1, H, W)
            
            mask_mode = interpolation if interpolation in ["nearest", "bilinear", "bicubic"] else "bilinear"
            resized_mask = do_resize(mask_expanded, resize_w, resize_h, mask_mode)
        else:
            resized_mask = torch.zeros((1, 1, resize_h, resize_w), device=image.device, dtype=torch.float32)

        # 8. 后处理：Fill (Crop) 或 Pad
        final_img = resized_img
        final_mask = resized_mask

        if method == "fill / crop":
            start_x = (resize_w - target_w) // 2
            start_y = (resize_h - target_h) // 2
            
            start_x = max(0, start_x)
            start_y = max(0, start_y)
            end_x = min(resize_w, start_x + target_w)
            end_y = min(resize_h, start_y + target_h)

            final_img = final_img[:, :, start_y:end_y, start_x:end_x]
            final_mask = final_mask[:, :, start_y:end_y, start_x:end_x]
            
        elif method == "pad (letterbox)":
            pad_w = target_w - resize_w
            pad_h = target_h - resize_h
            
            pad_left = pad_w // 2
            pad_right = pad_w - pad_left
            pad_top = pad_h // 2
            pad_bottom = pad_h - pad_top
            
            padding = (pad_left, pad_right, pad_top, pad_bottom)
            
            final_img = F.pad(final_img, padding, mode='constant', value=0)
            final_mask = F.pad(final_mask, padding, mode='constant', value=0)

        # 9. 恢复格式
        # 错误修复：使用 .permute() 而不是 .permutedim()
        output_image = final_img.permute(0, 2, 3, 1)
        output_mask = final_mask.squeeze(1)

        _, out_h, out_w, _ = output_image.shape

        return (output_image, output_mask, out_w, out_h)