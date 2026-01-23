import os
import torch
import numpy as np
from PIL import Image, ImageOps

class EHN_LoadImagesFromDir:
    """
    Loads images from a directory in a sequence (List).
    Because OUTPUT_IS_LIST is True, connecting this node to others will trigger
    a sequential execution (For Loop) for each image loaded.
    """
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "directory": ("STRING", {"default": ""}),
                "start_index": ("INT", {"default": 0, "min": 0, "step": 1}),
                "batch_count": ("INT", {"default": 1, "min": 1, "max": 100, "step": 1}),
                "sort_method": (["alphanumeric", "date_modified"],),
            }
        }

    RETURN_TYPES = ("IMAGE", "MASK", "STRING")
    RETURN_NAMES = ("Image", "Mask", "Filename")
    
    # 核心设置：设置为 True 表示输出的是一个列表，后续节点会对列表中的每一项单独运行一次
    OUTPUT_IS_LIST = (True, True, True)
    
    FUNCTION = "load_images"
    CATEGORY = "EaselHub/IO"

    def load_images(self, directory, start_index, batch_count, sort_method):
        if not os.path.isdir(directory):
            print(f"[EHN Error] Directory not found: {directory}")
            # 返回空的列表以防崩溃，虽然通常前端会报错
            return ([], [], [])

        # 1. 获取并筛选文件
        valid_extensions = {'.png', '.jpg', '.jpeg', '.webp', '.bmp', '.tiff'}
        files = [f for f in os.listdir(directory) 
                 if os.path.splitext(f)[1].lower() in valid_extensions]

        # 2. 排序
        if sort_method == "alphanumeric":
            files.sort()
        else:
            # 按修改时间排序
            files.sort(key=lambda x: os.path.getmtime(os.path.join(directory, x)))

        # 3. 计算切片范围
        total_files = len(files)
        if total_files == 0:
            print("[EHN Warning] No images found in directory.")
            return ([], [], [])
            
        start_index = max(0, min(start_index, total_files - 1))
        end_index = min(start_index + batch_count, total_files)
        
        selected_files = files[start_index:end_index]
        
        images_list = []
        masks_list = []
        filenames_list = []

        # 4. 逐个加载图片 (不进行 Batch 堆叠，而是存入 List)
        for filename in selected_files:
            image_path = os.path.join(directory, filename)
            
            i = Image.open(image_path)
            i = ImageOps.exif_transpose(i) # 修复旋转问题

            # 处理 Alpha 通道
            if 'A' in i.getbands():
                mask = np.array(i.getchannel('A')).astype(np.float32) / 255.0
                mask = 1. - torch.from_numpy(mask)
            else:
                mask = torch.zeros((i.size[1], i.size[0]), dtype=torch.float32, device="cpu")

            # 处理图像 RGB
            image = i.convert("RGB")
            image = np.array(image).astype(np.float32) / 255.0
            image = torch.from_numpy(image)[None,] # 增加 Batch 维度 [1, H, W, C]
            
            # 加入列表
            images_list.append(image)
            masks_list.append(mask)
            filenames_list.append(filename)

        print(f"[EHN] Loaded {len(images_list)} images from '{directory}' (Index {start_index} to {end_index-1})")
        
        # 返回 Tuple(List, List, List)
        return (images_list, masks_list, filenames_list)