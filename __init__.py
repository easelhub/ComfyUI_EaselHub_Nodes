from .nodes.image_tiling import EHN_ImageTiler, EHN_ImageMerger
from .nodes.image_resize import EHN_ImageResize
from .nodes.mask_process import EHN_MaskProcess
from .nodes.logic_math import EHN_MathExpression, EHN_NumberCompare
from .nodes.image_info import EHN_GetImageSize
from .nodes.system_opt import EHN_SystemOptimizer
from .nodes.image_compare import EHN_ImageCompare

NODE_CLASS_MAPPINGS = {
    "EHN_ImageTiler": EHN_ImageTiler,
    "EHN_ImageMerger": EHN_ImageMerger,
    "EHN_ImageResize": EHN_ImageResize,
    "EHN_MaskProcess": EHN_MaskProcess,
    "EHN_MathExpression": EHN_MathExpression,
    "EHN_NumberCompare": EHN_NumberCompare,
    "EHN_GetImageSize": EHN_GetImageSize,
    "EHN_SystemOptimizer": EHN_SystemOptimizer,
    "EHN_ImageCompare": EHN_ImageCompare
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "EHN_ImageTiler": "🧩 EHN Image Tiler",
    "EHN_ImageMerger": "🧩 EHN Image Merger",
    "EHN_ImageResize": "📏 EHN Image Resize",
    "EHN_MaskProcess": "🎭 EHN Mask Process",
    "EHN_MathExpression": "🧮 EHN Math Expression",
    "EHN_NumberCompare": "⚖️ EHN Number Compare",
    "EHN_GetImageSize": "📏 EHN Get Image Size",
    "EHN_SystemOptimizer": "🚀 EHN System Optimizer",
    "EHN_ImageCompare": "👀 EHN Image Compare"
}
WEB_DIRECTORY = "./web"
