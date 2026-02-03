from .nodes.ehn_variable import EHN_SetVariable, EHN_GetVariable
from .nodes.ehn_logic import EHN_Math, EHN_ExecutionOrder
from .nodes.ehn_prompt import EHN_PromptList
from .nodes.ehn_load_images import EHN_LoadImagesFromDir
from .nodes.ehn_image_resize import EHN_ImageResize
from .nodes.ehn_image_tile import EHN_ImageSplitTiles, EHN_ImageMergeTiles
from .nodes.ehn_image_compare import EHN_ImageCompare
from .nodes.ehn_image_stack import EHN_ImageStack
from .nodes.ehn_mask_ops import EHN_MaskFillHoles
from .nodes.ehn_teacache import EHN_TeaCache
from .nodes.ehn_utils import EHN_ImageSideCalc, EHN_FreeVRAM
from .nodes.ehn_llm import EHN_SiliconFlow, EHN_OpenRouter, EHN_DeepSeek, EHN_OpenAI, EHN_Gemini, EHN_CustomLLM, fetch_and_update_models
from aiohttp import web
import server

@server.PromptServer.instance.routes.post("/ehn/update_models")
async def update_models(request):
    try:
        data = await request.json()
        provider = data.get("provider")
        api_key = data.get("api_key")
        base_url = data.get("base_url")
        if not provider or not api_key: return web.json_response({"error": "Missing provider or api_key"}, status=400)
        
        # Run synchronous fetch in executor to avoid blocking main loop
        import asyncio
        loop = asyncio.get_event_loop()
        new_models = await loop.run_in_executor(None, fetch_and_update_models, provider, api_key, base_url)
        
        return web.json_response({"models": new_models})
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)

NODE_CLASS_MAPPINGS = {
    "EHN_SiliconFlow": EHN_SiliconFlow,
    "EHN_OpenRouter": EHN_OpenRouter,
    "EHN_DeepSeek": EHN_DeepSeek,
    "EHN_OpenAI": EHN_OpenAI,
    "EHN_Gemini": EHN_Gemini,
    "EHN_CustomLLM": EHN_CustomLLM,
    "EHN_SetVariable": EHN_SetVariable,
    "EHN_GetVariable": EHN_GetVariable,
    "EHN_Math": EHN_Math,
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
    "EHN_SiliconFlow":     "🤖 LLM Prompt Gen - SiliconFlow",
    "EHN_OpenRouter":      "🌌 LLM Prompt Gen - OpenRouter",
    "EHN_DeepSeek":        "🐋 LLM Prompt Gen - DeepSeek",
    "EHN_OpenAI":          "🧠 LLM Prompt Gen - OpenAI",
    "EHN_Gemini":          "💎 LLM Prompt Gen - Google Gemini",
    "EHN_CustomLLM":       "🛠️ LLM Prompt Gen - Custom/Local",
    "EHN_SetVariable":     "📡 Set Global Variable",
    "EHN_GetVariable":     "📶 Get Global Variable",
    "EHN_Math":            "🧮 Math Expression",
    "EHN_ExecutionOrder":  "🚦 Execution Order Control",
    "EHN_PromptList":      "📝 Prompt Mixer",
    "EHN_LoadImagesFromDir": "📂 Batch Image Loader",
    "EHN_ImageResize":     "🔧 Image Resize & Crop",
    "EHN_ImageSplitTiles": "🧱 Split Image to Tiles",
    "EHN_ImageMergeTiles": "🏗️ Merge Tiles to Image",
    "EHN_ImageCompare":    "⚖️ Image Compare",
    "EHN_ImageStack":      "🥞 Image Stack (Grid/Strip)",
    "EHN_MaskFillHoles":   "🕳️ Mask Operations",
    "EHN_TeaCache":        "🍵 TeaCache Optimization",
    "EHN_ImageSideCalc":   "📏 Get Image Dimensions",
    "EHN_FreeVRAM":        "🧹 VRAM Cleaner"
}

WEB_DIRECTORY = "./web"
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]