import os
import sys
import subprocess
import importlib.util

def auto_install():
    req = os.path.join(os.path.dirname(__file__), "requirements.txt")
    if not os.path.exists(req): return
    with open(req, 'r') as f:
        deps = [x.strip().split('=')[0].split('>')[0].split('<')[0] for x in f if x.strip()]
    
    map_name = {"Pillow": "PIL"}
    if any(importlib.util.find_spec(map_name.get(d, d)) is None for d in deps):
        try: subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", req])
        except Exception as e: print(f"EHN Auto-Install Failed: {e}")

auto_install()

from .nodes.ehn_image_tiling import EHN_ImageTiler, EHN_ImageMerger
from .nodes.ehn_image_resize import EHN_ImageResize
from .nodes.ehn_mask_ops import EHN_MaskProcessor
from .nodes.ehn_image_utils import EHN_GetImageSize
from .nodes.ehn_number_ops import EHN_MathExpression, EHN_NumberCompare
from .nodes.ehn_system_utils import EHN_SystemOptimizer
from .nodes.ehn_image_comparison import EHN_ImageComparison
from .nodes.ehn_text_ops import EHN_PromptList, EHN_PromptMix
from .nodes.ehn_ai_generator import EHN_AIGenerator, EHN_OpenAIGenerator, EHN_OllamaGenerator
from .nodes.ehn_image_loader import EHN_ImageLoader
from .nodes.ehn_florence2 import EHN_Florence2PromptGen
from .nodes import ehn_schedulers

NODE_CLASS_MAPPINGS = {
    "EHN_Florence2PromptGen": EHN_Florence2PromptGen,
    "EHN_ImageLoader": EHN_ImageLoader,
    "EHN_ImageTiler": EHN_ImageTiler,
    "EHN_ImageMerger": EHN_ImageMerger,
    "EHN_ImageResize": EHN_ImageResize,
    "EHN_MaskProcessor": EHN_MaskProcessor,
    "EHN_GetImageSize": EHN_GetImageSize,
    "EHN_MathExpression": EHN_MathExpression,
    "EHN_NumberCompare": EHN_NumberCompare,
    "EHN_SystemOptimizer": EHN_SystemOptimizer,
    "EHN_ImageComparison": EHN_ImageComparison,
    "EHN_PromptList": EHN_PromptList,
    "EHN_PromptMix": EHN_PromptMix,
    "EHN_AIGenerator": EHN_AIGenerator,
    "EHN_OpenAIGenerator": EHN_OpenAIGenerator,
    "EHN_OllamaGenerator": EHN_OllamaGenerator,
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
    "EHN_ImageComparison": "👁️EHN Image Comparison",
    "EHN_PromptList": "📝EHN Prompt List",
    "EHN_PromptMix": "🔗EHN Prompt Mix",
    "EHN_AIGenerator": "🤖EHN AI Generator",
    "EHN_OpenAIGenerator": "🤖EHN OpenAI Generator",
    "EHN_OllamaGenerator": "🤖EHN Ollama Generator",
    "EHN_ImageLoader": "📂EHN Image Loader",
    "EHN_Florence2PromptGen": "📝EHN Florence2 Prompt",
}

WEB_DIRECTORY = "./web"
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]