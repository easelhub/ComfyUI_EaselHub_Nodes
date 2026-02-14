import torch
import numpy as np
from color_matcher import ColorMatcher

class EHN_ColorMatch:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image_ref": ("IMAGE",),      # 参考图（提供配色）
                "image_target": ("IMAGE",),   # 目标图（需要改色）
                "method": ([
                    "mkl", 
                    "hm", 
                    "reinhard", 
                    "mvgd", 
                    "hm-mvgd-hm", 
                    "hm-mkl-hm"
                ], {"default": "mkl"}),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "color_match"
    CATEGORY = "EasyUse_Ported"  # 你可以修改为你项目中的分类名称

    def color_match(self, image_ref, image_target, method):
        # 1. 准备 ColorMatcher 实例
        cm = ColorMatcher()
        
        # 2. ComfyUI Tensor (B,H,W,C) -> Numpy (B,H,W,C)
        # 注意：ComfyUI 图片是 0-1 float，color-matcher 最好处理 0-255 uint8
        target_images = image_target.cpu().numpy()
        ref_images = image_ref.cpu().numpy()

        # 确保数据至少是 4D (Batch, Height, Width, Channel)
        if target_images.ndim == 3: target_images = target_images[None, ...]
        if ref_images.ndim == 3: ref_images = ref_images[None, ...]

        batch_size = target_images.shape[0]
        out_images = []

        # 3. 批处理循环
        for i in range(batch_size):
            # 获取单张图片
            target_img = target_images[i]
            # 如果参考图数量少于目标图，则循环使用参考图
            ref_img = ref_images[i % ref_images.shape[0]]

            # 转换为 uint8 [0, 255]
            # 使用 clip 确保数值不越界，防止颜色崩坏
            target_img_uint8 = (target_img * 255).clip(0, 255).astype(np.uint8)
            ref_img_uint8 = (ref_img * 255).clip(0, 255).astype(np.uint8)

            try:
                # 4. 核心调用：执行色彩迁移
                # src=要改变的图, ref=参考颜色的图
                matched_img_uint8 = cm.transfer(
                    src=target_img_uint8, 
                    ref=ref_img_uint8, 
                    method=method
                )
                
                # 防御性编程：如果算法返回 None（极少数情况），回退到原图
                if matched_img_uint8 is None:
                    matched_img_uint8 = target_img_uint8
                    
            except Exception as e:
                print(f"[EHN_ColorMatch] Error processing batch {i}: {e}")
                matched_img_uint8 = target_img_uint8

            # 5. 转回 Float32 [0, 1]
            matched_img = matched_img_uint8.astype(np.float32) / 255.0
            out_images.append(matched_img)

        # 6. 堆叠回 Tensor 并返回
        if not out_images:
            return (image_target,)
            
        result = torch.from_numpy(np.array(out_images))
        return (result,)