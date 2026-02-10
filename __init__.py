from .nodes.ehn_image_resize import EHN_ImageResize
from .nodes.ehn_image_tiling import EHN_ImageTiler, EHN_ImageMerger
from .nodes.ehn_image_utils import EHN_GetImageSize
from .nodes.ehn_mask_ops import EHN_MaskProcessor
from .nodes.ehn_number_ops import EHN_MathExpression, EHN_NumberCompare
from .nodes.ehn_text_ops import EHN_PromptList, EHN_PromptMix
from .nodes.ehn_system_utils import EHN_SystemOptimizer, EHN_SchedulerInjector
from .nodes.ehn_image_comparison import EHN_ImageComparison
from .nodes.ehn_ai_generator import EHN_AIGenerator, EHN_OpenAIGenerator, EHN_OllamaGenerator
from .nodes.ehn_florence2 import EHN_Florence2PromptGen
from .nodes.ehn_wd14 import EHN_WD14Tagger
from .nodes.ehn_image_loader import EHN_ImageLoader

NODE_CLASS_MAPPINGS = {
    "EHN_ImageResize": EHN_ImageResize,
    "EHN_ImageTiler": EHN_ImageTiler,
    "EHN_ImageMerger": EHN_ImageMerger,
    "EHN_GetImageSize": EHN_GetImageSize,
    "EHN_MaskProcessor": EHN_MaskProcessor,
    "EHN_MathExpression": EHN_MathExpression,
    "EHN_NumberCompare": EHN_NumberCompare,
    "EHN_PromptList": EHN_PromptList,
    "EHN_PromptMix": EHN_PromptMix,
    "EHN_SystemOptimizer": EHN_SystemOptimizer,
    "EHN_SchedulerInjector": EHN_SchedulerInjector,
    "EHN_ImageComparison": EHN_ImageComparison,
    "EHN_AIGenerator": EHN_AIGenerator,
    "EHN_OpenAIGenerator": EHN_OpenAIGenerator,
    "EHN_OllamaGenerator": EHN_OllamaGenerator,
    "EHN_Florence2PromptGen": EHN_Florence2PromptGen,
    "EHN_WD14Tagger": EHN_WD14Tagger,
    "EHN_ImageLoader": EHN_ImageLoader,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "EHN_ImageResize": "🧩 EHN Image Resize",
    "EHN_ImageTiler": "🧩 EHN Image Tiler",
    "EHN_ImageMerger": "🧩 EHN Image Merger",
    "EHN_GetImageSize": "🧩 EHN Get Image Size",
    "EHN_MaskProcessor": "🎭 EHN Mask Processor",
    "EHN_MathExpression": "🔢 EHN Math Expression",
    "EHN_NumberCompare": "🔢 EHN Number Compare",
    "EHN_PromptList": "📝 EHN Prompt List",
    "EHN_PromptMix": "📝 EHN Prompt Mix",
    "EHN_SystemOptimizer": "⚙️ EHN System Optimizer",
    "EHN_SchedulerInjector": "⚙️ EHN Scheduler Injector",
    "EHN_ImageComparison": "🖼️ EHN Image Comparison",
    "EHN_AIGenerator": "🤖 EHN AI Generator",
    "EHN_OpenAIGenerator": "🤖 EHN OpenAI Generator",
    "EHN_OllamaGenerator": "🤖 EHN Ollama Generator",
    "EHN_Florence2PromptGen": "👁️ EHN Florence2 PromptGen",
    "EHN_WD14Tagger": "🏷️ EHN WD14 Tagger",
    "EHN_ImageLoader": "📂 EHN Image Loader",
}

WEB_DIRECTORY = "./web"
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
