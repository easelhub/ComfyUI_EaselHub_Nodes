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
    def INPUT_TYPES(s):
        return {"required": {"image": ("IMAGE",), "side": (["Longest", "Shortest"],)}}
    RETURN_TYPES = ("INT", "INT", "INT")
    RETURN_NAMES = ("Side", "Width", "Height")
    FUNCTION = "calc"
    CATEGORY = "EaselHub/Utils"
    def calc(self, image, side):
        h, w = image.shape[1:3]
        return ({"Longest": max(h, w)}.get(side, min(h, w)), w, h)

class EHN_FreeVRAM:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {"mode": (["Soft", "Hard"],)}, "optional": {"any_input": (any_type,)}}
    RETURN_TYPES = (any_type,)
    FUNCTION = "run"
    CATEGORY = "EaselHub/Utils"
    OUTPUT_NODE = True
    def run(self, mode, any_input=None):
        try:
            for obj in gc.get_objects():
                if hasattr(obj, "tc_logic"): delattr(obj, "tc_logic")
        except: pass
        gc.collect()
        torch.cuda.empty_cache()
        try: torch.cuda.ipc_collect()
        except: pass
        if mode == "Hard": comfy.model_management.unload_all_models()
        comfy.model_management.soft_empty_cache()
        return (any_input,)
