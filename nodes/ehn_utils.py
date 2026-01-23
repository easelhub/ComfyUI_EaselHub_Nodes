import torch
import gc
import comfy.model_management

class EHN_ImageSideCalc:
    """
    获取图片的长边、短边、宽度或高度。
    """
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "side": (["Longest", "Shortest", "Width", "Height"], {"default": "Longest"}),
            }
        }

    RETURN_TYPES = ("INT",)
    RETURN_NAMES = ("value",)
    FUNCTION = "get_side"
    CATEGORY = "EaselHub/Utils"

    def get_side(self, image, side):
        # ComfyUI Image shape: [Batch, Height, Width, Channels]
        _, h, w, _ = image.shape
        
        value = 0
        if side == "Width":
            value = w
        elif side == "Height":
            value = h
        elif side == "Longest":
            value = max(h, w)
        elif side == "Shortest":
            value = min(h, w)
            
        return (value,)

# 定义通用类型用于 VRAM 清理节点的直通
class AnyType(str):
    def __ne__(self, __value: object) -> bool:
        return False
any_type = AnyType("*")

class EHN_FreeVRAM:
    """
    清理显存和缓存，支持直通模式（串联在工作流中）。
    """
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "mode": (["Soft (Empty Cache)", "Hard (Unload Models)"], {"default": "Soft (Empty Cache)"}),
            },
            "optional": {
                "any_input": (any_type,), # 允许连接任何节点以控制执行顺序
            }
        }

    RETURN_TYPES = (any_type,)
    RETURN_NAMES = ("output_passthrough",)
    FUNCTION = "clear_vram"
    CATEGORY = "EaselHub/Utils"
    OUTPUT_NODE = True

    def clear_vram(self, mode, any_input=None):
        # 1. Python 垃圾回收
        gc.collect()
        
        # 2. PyTorch 显存清理
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()
            
        # 3. ComfyUI 模型管理清理
        if mode == "Hard (Unload Models)":
            # 强制卸载所有模型
            comfy.model_management.unload_all_models()
            comfy.model_management.soft_empty_cache()
            print("[EHN] VRAM Cleared: Models Unloaded & Cache Emptied.")
        else:
            # 仅清理缓存
            comfy.model_management.soft_empty_cache()
            print("[EHN] VRAM Cleared: Cache Emptied.")

        return (any_input,)