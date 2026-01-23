import torch
import torch.nn.functional as F
import math

# 定义 Tile 信息传输的类型
class AnyType(str):
    def __ne__(self, __value: object) -> bool:
        return False
any_type = AnyType("*")

class EHN_ImageSplitTiles:
    """
    大图分块节点：
    1. 将大图切分为指定大小的小块 (Batch)。
    2. 自动计算 Padding 保证整除。
    3. 支持 Overlap (重叠) 以防止接缝。
    4. [修改] 移除了独立的宽高输出端口，保持界面简洁。
    """
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "tile_size": ("INT", {"default": 512, "min": 128, "max": 8192, "step": 64}),
                "overlap": ("INT", {"default": 64, "min": 0, "max": 512, "step": 8}),
            }
        }

    RETURN_TYPES = ("IMAGE", any_type)
    RETURN_NAMES = ("tiles_batch", "tile_info")
    FUNCTION = "split_image"
    CATEGORY = "EaselHub/Tiling"

    def split_image(self, image, tile_size, overlap):
        # image shape: [B, H, W, C]
        if image.shape[0] > 1:
            print("[EHN Warning] SplitTiles received batch > 1, using only first image.")
            image = image[0:1]
        
        b, h, w, c = image.shape
        
        # 1. 基础参数计算
        stride = tile_size - overlap
        if stride <= 0:
            raise ValueError("Overlap must be smaller than Tile Size.")

        # 2. 计算需要的行列数
        cols = math.ceil((w - overlap) / stride)
        rows = math.ceil((h - overlap) / stride)
        
        cols = max(1, cols)
        rows = max(1, rows)

        # 3. 计算 Pad 后的大小
        pad_w = (cols - 1) * stride + tile_size
        pad_h = (rows - 1) * stride + tile_size
        
        # 4. Padding 图片
        img_p = image.permute(0, 3, 1, 2) # [1, C, H, W]
        
        pad_right = pad_w - w
        pad_bottom = pad_h - h
        
        if pad_right > 0 or pad_bottom > 0:
            img_p = F.pad(img_p, (0, pad_right, 0, pad_bottom), mode='reflect')
        
        # 5. 切片提取
        tiles = []
        for r in range(rows):
            for c_idx in range(cols):
                y_start = r * stride
                x_start = c_idx * stride
                y_end = y_start + tile_size
                x_end = x_start + tile_size
                
                # Crop: [B, C, H, W]
                tile = img_p[:, :, y_start:y_end, x_start:x_end]
                # 转回 [B, H, W, C]
                tile = tile.permute(0, 2, 3, 1)
                tiles.append(tile)

        # 6. 合并为 Batch [N, H, W, C]
        tiles_batch = torch.cat(tiles, dim=0)

        # 7. 封装元数据
        tile_info = {
            "original_width": w,
            "original_height": h,
            "pad_width": pad_w,
            "pad_height": pad_h,
            "tile_size": tile_size,
            "overlap": overlap,
            "stride": stride,
            "rows": rows,
            "cols": cols
        }

        # 修改：只返回 tiles 和 info
        return (tiles_batch, tile_info)


class EHN_ImageMergeTiles:
    """
    分块合并节点：
    1. 接收处理后的小块 Batch。
    2. 自动检测输入 Tile 的尺寸变化 (Upscale 支持)。
    3. 动态调整 Overlap 和 Canvas 尺寸。
    4. 使用加权遮罩 (Feather Mask) 融合重叠区域。
    """
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE",),
                "tile_info": (any_type,),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("merged_image",)
    FUNCTION = "merge_images"
    CATEGORY = "EaselHub/Tiling"

    def merge_images(self, images, tile_info):
        if not isinstance(tile_info, dict):
            print("[EHN Error] Invalid tile_info.")
            return (images,)

        # 1. 获取当前 Tile 的实际尺寸 (支持 Upscale)
        # images: [N, H, W, C]
        curr_h, curr_w = images.shape[1], images.shape[2]
        
        # 2. 获取原始分块信息
        old_tile_size = tile_info["tile_size"]
        old_overlap = tile_info["overlap"]
        rows = tile_info["rows"]
        cols = tile_info["cols"]
        old_orig_w = tile_info["original_width"]
        old_orig_h = tile_info["original_height"]

        # 3. 计算缩放比例
        scale_h = curr_h / old_tile_size
        scale_w = curr_w / old_tile_size

        # 4. 根据比例重新计算合并参数
        new_overlap_h = int(old_overlap * scale_h)
        new_overlap_w = int(old_overlap * scale_w)
        
        new_stride_h = curr_h - new_overlap_h
        new_stride_w = curr_w - new_overlap_w
        
        new_pad_h = (rows - 1) * new_stride_h + curr_h
        new_pad_w = (cols - 1) * new_stride_w + curr_w
        
        new_orig_h = int(old_orig_h * scale_h)
        new_orig_w = int(old_orig_w * scale_w)

        # 5. 准备画布
        device = images.device
        canvas = torch.zeros((3, new_pad_h, new_pad_w), device=device, dtype=torch.float32)
        weight_map = torch.zeros((1, new_pad_h, new_pad_w), device=device, dtype=torch.float32)
        
        # 6. 创建加权遮罩 (Feather Mask)
        mask = torch.ones((1, curr_h, curr_w), device=device, dtype=torch.float32)
        
        if new_overlap_h > 0:
            ramp_h = torch.linspace(0.0, 1.0, new_overlap_h, device=device).view(-1, 1)
            mask[:, :new_overlap_h, :] *= ramp_h
            mask[:, -new_overlap_h:, :] *= ramp_h.flip(0)
            
        if new_overlap_w > 0:
            ramp_w = torch.linspace(0.0, 1.0, new_overlap_w, device=device).view(1, -1)
            mask[:, :, :new_overlap_w] *= ramp_w
            mask[:, :, -new_overlap_w:] *= ramp_w.flip(1)

        # 7. 循环拼贴
        batch_imgs = images.permute(0, 3, 1, 2) # [N, C, H, W]
        
        idx = 0
        for r in range(rows):
            for c in range(cols):
                if idx >= batch_imgs.shape[0]: 
                    break
                
                img_tile = batch_imgs[idx] # [C, H, W]
                
                y_start = r * new_stride_h
                x_start = c * new_stride_w
                y_end = y_start + curr_h
                x_end = x_start + curr_w
                
                canvas[:, y_start:y_end, x_start:x_end] += img_tile * mask
                weight_map[:, y_start:y_end, x_start:x_end] += mask
                
                idx += 1
                
        # 8. 归一化与裁剪
        weight_map = torch.clamp(weight_map, min=1e-5)
        final_img = canvas / weight_map
        
        crop_h = min(new_orig_h, final_img.shape[1])
        crop_w = min(new_orig_w, final_img.shape[2])
        
        final_img = final_img[:, :crop_h, :crop_w]
        
        # 9. 输出
        final_img = final_img.permute(1, 2, 0).unsqueeze(0)
        
        return (final_img,)