from .nodes.image_tiling import EHN_ImageTiler, EHN_ImageMerger
from .nodes.image_resize import EHN_ImageResize
from .nodes.mask_process import EHN_MaskProcess

NODE_CLASS_MAPPINGS = {
    "EHN_ImageTiler": EHN_ImageTiler,
    "EHN_ImageMerger": EHN_ImageMerger,
    "EHN_ImageResize": EHN_ImageResize,
    "EHN_MaskProcess": EHN_MaskProcess
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "EHN_ImageTiler": "🧩 EHN Image Tiler",
    "EHN_ImageMerger": "🧩 EHN Image Merger",
    "EHN_ImageResize": "📏 EHN Image Resize",
    "EHN_MaskProcess": "🎭 EHN Mask Process"
}
