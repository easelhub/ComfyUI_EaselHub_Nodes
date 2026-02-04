import torch
import gc
import numpy as np
import comfy.model_management

class AnyType(str):
    def __ne__(self, o): return False
    def __eq__(self, o): return True

any_type = AnyType("*")

def fill_mask_holes(mask):
    try: from scipy.ndimage import binary_fill_holes
    except: return mask
    if mask is None: return None
    device = mask.device
    mask_cpu = mask.cpu()
    if mask.dim() == 2:
         m = mask_cpu.numpy()
         f = binary_fill_holes(m > 0.5).astype(np.float32)
         return torch.from_numpy(f).to(device)
    elif mask.dim() == 3:
        out = []
        for i in range(mask.shape[0]):
            m = mask_cpu[i].numpy()
            f = binary_fill_holes(m > 0.5).astype(np.float32)
            out.append(torch.from_numpy(f))
        return torch.stack(out).to(device)
    elif mask.dim() == 4 and mask.shape[1] == 1:
        out = []
        for i in range(mask.shape[0]):
            m = mask_cpu[i, 0].numpy()
            f = binary_fill_holes(m > 0.5).astype(np.float32)
            out.append(torch.from_numpy(f))
        return torch.stack(out).unsqueeze(1).to(device)
    return mask

class EHN_ImageSideCalc:
    @classmethod
    def INPUT_TYPES(s): return {"required": {"image": ("IMAGE",), "side": (["Longest", "Shortest"],)}}
    RETURN_TYPES = ("INT", "INT", "INT", "FLOAT", "STRING")
    RETURN_NAMES = ("Side", "Width", "Height", "Aspect Ratio", "Orientation")
    FUNCTION = "calc"
    CATEGORY = "EaselHub/Utils"
    def calc(self, image, side):
        h, w = image.shape[1:3]
        return (max(h, w) if side == "Longest" else min(h, w), w, h, w / h, "Landscape" if w > h else "Portrait" if h > w else "Square")

class EHN_FreeVRAM:
    @classmethod
    def INPUT_TYPES(s): return {"required": {}, "optional": {"any_input": (any_type,)}}
    RETURN_TYPES = (any_type,)
    FUNCTION = "run"
    CATEGORY = "EaselHub/Utils"
    OUTPUT_NODE = True
    def run(self, any_input=None):
        try:
            for o in gc.get_objects():
                if hasattr(o, "tc_logic"): delattr(o, "tc_logic")
        except: pass
        gc.collect()
        if hasattr(comfy.model_management, "cleanup_models"): comfy.model_management.cleanup_models()
        comfy.model_management.soft_empty_cache()
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()
        return (any_input,)
