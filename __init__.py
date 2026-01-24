from .nodes.ehn_generation import EHN_SmartResolution
from .nodes.ehn_logic_data import EHN_SetVariable, EHN_GetVariable, EHN_AnySwitch, EHN_BinaryMath, EHN_PromptList
from .nodes.ehn_io import EHN_LoadImagesFromDir
from .nodes.ehn_image_ops import EHN_ImageResize, EHN_ImageSplitTiles, EHN_ImageMergeTiles
from .nodes.ehn_utils import EHN_ImageSideCalc, EHN_FreeVRAM

NODE_CLASS_MAPPINGS = {
    "EHN_SmartResolution": EHN_SmartResolution,
    
    "EHN_SetVariable": EHN_SetVariable,
    "EHN_GetVariable": EHN_GetVariable,
    "EHN_AnySwitch": EHN_AnySwitch,
    "EHN_BinaryMath": EHN_BinaryMath,
    "EHN_PromptList": EHN_PromptList,
    
    "EHN_LoadImagesFromDir": EHN_LoadImagesFromDir,
    
    "EHN_ImageResize": EHN_ImageResize,
    "EHN_ImageSplitTiles": EHN_ImageSplitTiles,
    "EHN_ImageMergeTiles": EHN_ImageMergeTiles,
    
    "EHN_ImageSideCalc": EHN_ImageSideCalc,
    "EHN_FreeVRAM": EHN_FreeVRAM
}

NODE_DISPLAY_NAME_MAPPINGS = {
    # 🔍 Generation
    "EHN_SmartResolution": "🔍 EHN Aspect Ratio & Latent",
    
    # 🧠 Logic
    "EHN_SetVariable":     "📡 EHN Set Global Var",
    "EHN_GetVariable":     "📶 EHN Get Global Var",
    "EHN_AnySwitch":       "🔀 EHN Universal Switch",
    "EHN_BinaryMath":      "🧮 EHN Math Operations",
    "EHN_PromptList":      "📝 EHN Prompt Mixer",
    
    # 📂 IO
    "EHN_LoadImagesFromDir": "📂 EHN Batch Image Loader",
    
    # 🎨 Image Ops
    "EHN_ImageResize":     "🔧 EHN Image Resize & Crop",
    "EHN_ImageSplitTiles": "🧱 EHN Tile Split (Tiling)",
    "EHN_ImageMergeTiles": "🏗️ EHN Tile Merge (Blending)",
    
    # 🛠️ Utils
    "EHN_ImageSideCalc":   "📏 EHN Get Image Dimensions",
    "EHN_FreeVRAM":        "🧹 EHN VRAM Cleaner / Cache"
}

WEB_DIRECTORY = "./js"

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]