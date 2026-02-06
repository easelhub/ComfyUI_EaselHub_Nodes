from .nodes.ehn_image_tiling import EHN_ImageTiler, EHN_ImageMerger
from .nodes.ehn_image_resize import EHN_ImageResize
from .nodes.ehn_mask_ops import EHN_MaskProcessor
from .nodes.ehn_image_utils import EHN_GetImageSize
from .nodes.ehn_number_ops import EHN_MathExpression, EHN_NumberCompare
from .nodes.ehn_system_utils import EHN_SystemOptimizer
from .nodes.ehn_image_comparison import EHN_ImageComparison

NODE_CLASS_MAPPINGS = {
    "EHN_ImageTiler": EHN_ImageTiler,
    "EHN_ImageMerger": EHN_ImageMerger,
    "EHN_ImageResize": EHN_ImageResize,
    "EHN_MaskProcessor": EHN_MaskProcessor,
    "EHN_GetImageSize": EHN_GetImageSize,
    "EHN_MathExpression": EHN_MathExpression,
    "EHN_NumberCompare": EHN_NumberCompare,
    "EHN_SystemOptimizer": EHN_SystemOptimizer,
    "EHN_ImageComparison": EHN_ImageComparison
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "EHN_ImageTiler": "🧩EHN Image Tiler",
    "EHN_ImageMerger": "🧩EHN Image Merger",
    "EHN_ImageResize": "📐EHN Image Resize",
    "EHN_MaskProcessor": "🎭EHN Mask Editor",
    "EHN_GetImageSize": "📏EHN Get Image Size",
    "EHN_MathExpression": "🔢EHN Math Expression",
    "EHN_NumberCompare": "⚖️EHN Number Compare",
    "EHN_SystemOptimizer": "🚀EHN System Optimizer",
    "EHN_ImageComparison": "👁️EHN Image Comparison"
}

WEB_DIRECTORY = "./web"

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]

print("\033[34mComfyUI EaselHub Nodes: \033[92mLoaded\033[0m")
