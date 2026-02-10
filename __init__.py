from .nodes.image_tiling import EHN_ImageTiler, EHN_ImageMerger
from .nodes.image_resize import EHN_ImageResize

NODE_CLASS_MAPPINGS = {
    "EHN_ImageTiler": EHN_ImageTiler,
    "EHN_ImageMerger": EHN_ImageMerger,
    "EHN_ImageResize": EHN_ImageResize
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "EHN_ImageTiler": "🧩 EHN Image Tiler",
    "EHN_ImageMerger": "🧩 EHN Image Merger",
    "EHN_ImageResize": "📏 EHN Image Resize"
}
