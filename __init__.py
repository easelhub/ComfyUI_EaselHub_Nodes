from .nodes.ehn_variable import EHN_SetVariable, EHN_GetVariable
from .nodes.ehn_logic import EHN_InputToNumber, EHN_BinaryMath, EHN_SimpleMath, EHN_ExecutionOrder
from .nodes.ehn_prompt import EHN_PromptList
from .nodes.ehn_load_images import EHN_LoadImagesFromDir
from .nodes.ehn_image_resize import EHN_ImageResize
from .nodes.ehn_image_tile import EHN_ImageSplitTiles, EHN_ImageMergeTiles
from .nodes.ehn_image_compare import EHN_ImageCompare
from .nodes.ehn_image_stack import EHN_ImageStack
from .nodes.ehn_mask_ops import EHN_MaskFillHoles
from .nodes.ehn_teacache import EHN_TeaCache
from .nodes.ehn_utils import EHN_ImageSideCalc, EHN_FreeVRAM
from .nodes.ehn_llm import EHN_SiliconFlow, EHN_OpenRouter, EHN_DeepSeek, EHN_OpenAI, EHN_Gemini, EHN_CustomLLM

NODE_CLASS_MAPPINGS = {
    "EHN_SiliconFlow": EHN_SiliconFlow,
    "EHN_OpenRouter": EHN_OpenRouter,
    "EHN_DeepSeek": EHN_DeepSeek,
    "EHN_OpenAI": EHN_OpenAI,
    "EHN_Gemini": EHN_Gemini,
    "EHN_CustomLLM": EHN_CustomLLM,
    "EHN_SetVariable": EHN_SetVariable,
    "EHN_GetVariable": EHN_GetVariable,
    "EHN_InputToNumber": EHN_InputToNumber,
    "EHN_BinaryMath": EHN_BinaryMath,
    "EHN_SimpleMath": EHN_SimpleMath,
    "EHN_ExecutionOrder": EHN_ExecutionOrder,
    "EHN_PromptList": EHN_PromptList,
    "EHN_LoadImagesFromDir": EHN_LoadImagesFromDir,
    "EHN_ImageResize": EHN_ImageResize,
    "EHN_ImageSplitTiles": EHN_ImageSplitTiles,
    "EHN_ImageMergeTiles": EHN_ImageMergeTiles,
    "EHN_ImageCompare": EHN_ImageCompare,
    "EHN_ImageStack": EHN_ImageStack,
    "EHN_MaskFillHoles": EHN_MaskFillHoles,
    "EHN_TeaCache": EHN_TeaCache,
    "EHN_ImageSideCalc": EHN_ImageSideCalc,
    "EHN_FreeVRAM": EHN_FreeVRAM
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "EHN_SiliconFlow":     "🤖 EHN LLM Prompt Gen (SiliconFlow)",
    "EHN_OpenRouter":      "🌌 EHN LLM Prompt Gen (OpenRouter)",
    "EHN_DeepSeek":        "🐋 EHN LLM Prompt Gen (DeepSeek)",
    "EHN_OpenAI":          "🧠 EHN LLM Prompt Gen (OpenAI)",
    "EHN_Gemini":          "💎 EHN LLM Prompt Gen (Google Gemini)",
    "EHN_CustomLLM":       "🛠️ EHN LLM Prompt Gen (Custom/Local)",
    "EHN_SetVariable":     "📡 EHN Set Global Var",
    "EHN_GetVariable":     "📶 EHN Get Global Var",
    "EHN_InputToNumber":   "🔢 EHN Cast to Number",
    "EHN_BinaryMath":      "🧮 EHN Math Operations",
    "EHN_SimpleMath":      "📐 EHN Expression Math",
    "EHN_ExecutionOrder":  "🚦 EHN Execution Order Control",
    "EHN_PromptList":      "📝 EHN Prompt Mixer",
    "EHN_LoadImagesFromDir": "📂 EHN Batch Image Loader",
    "EHN_ImageResize":     "🔧 EHN Image Resize & Crop",
    "EHN_ImageSplitTiles": "🧱 EHN Tile Split (Tiling)",
    "EHN_ImageMergeTiles": "🏗️ EHN Tile Merge (Blending)",
    "EHN_ImageCompare":    "⚖️ EHN Image Compare",
    "EHN_ImageStack":      "🥞 EHN Image Stack (Merge More)",
    "EHN_MaskFillHoles":   "🕳️ EHN Mask Fill Holes",
    "EHN_TeaCache":        "🍵 EHN TeaCache Acceleration",
    "EHN_ImageSideCalc":   "📏 EHN Get Image Dimensions",
    "EHN_FreeVRAM":        "🧹 EHN VRAM Cleaner / Cache"
}

WEB_DIRECTORY = "./js"
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]