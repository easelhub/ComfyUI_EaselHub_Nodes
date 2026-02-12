from .py.ehn_image_comparer import EHN_ImageComparer
from .py.ehn_image_tile import EHN_ImageTileBatch, EHN_ImageAssembly
from .py.ehn_florence2_tagger import EHN_Florence2Tagger

NODE_CLASS_MAPPINGS = {
    "EHN_ImageComparer": EHN_ImageComparer,
    "EHN_ImageTileBatch": EHN_ImageTileBatch,
    "EHN_ImageAssembly": EHN_ImageAssembly,
    "EHN_Florence2Tagger": EHN_Florence2Tagger
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "EHN_ImageComparer": "🖼️ EHN Image Comparer",
    "EHN_ImageTileBatch": "🧩 EHN Image Tile Batch",
    "EHN_ImageAssembly": "🧩 EHN Image Assembly",
    "EHN_Florence2Tagger": "🏷️ EHN Florence2 Tagger"
}

WEB_DIRECTORY = "./js"

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
