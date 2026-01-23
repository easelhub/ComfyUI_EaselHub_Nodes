from .nodes.ehn_smart_resolution import EHN_SmartResolution
from .nodes.ehn_set_get import EHN_SetVariable, EHN_GetVariable
from .nodes.ehn_image_loader import EHN_LoadImagesFromDir
from .nodes.ehn_math_logic import EHN_BinaryMath
from .nodes.ehn_utils import EHN_ImageSideCalc, EHN_FreeVRAM
from .nodes.ehn_image_resize import EHN_ImageResize
from .nodes.ehn_tiling import EHN_ImageSplitTiles, EHN_ImageMergeTiles

NODE_CLASS_MAPPINGS = {
    "EHN_SmartResolution": EHN_SmartResolution,
    "EHN_SetVariable": EHN_SetVariable,
    "EHN_GetVariable": EHN_GetVariable,
    "EHN_LoadImagesFromDir": EHN_LoadImagesFromDir,
    "EHN_BinaryMath": EHN_BinaryMath,
    "EHN_ImageSideCalc": EHN_ImageSideCalc,
    "EHN_FreeVRAM": EHN_FreeVRAM,
    "EHN_ImageResize": EHN_ImageResize,
    "EHN_ImageSplitTiles": EHN_ImageSplitTiles,
    "EHN_ImageMergeTiles": EHN_ImageMergeTiles
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "EHN_SmartResolution": "🔍 EHN Smart Resolution",
    "EHN_SetVariable": "📡 EHN Set Var",
    "EHN_GetVariable": "📶 EHN Get Var",
    "EHN_LoadImagesFromDir": "📂 EHN Batch Loader",
    "EHN_BinaryMath": "🧮 EHN Math & Logic",
    "EHN_ImageSideCalc": "📏 EHN Get Image Side",
    "EHN_FreeVRAM": "🧹 EHN Free VRAM/Cache",
    "EHN_ImageResize": "🔧 EHN Image Resize",
    "EHN_ImageSplitTiles": "🧱 EHN Split Image",
    "EHN_ImageMergeTiles": "🏗️ EHN Merge Image"
}

WEB_DIRECTORY = "./js"

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]