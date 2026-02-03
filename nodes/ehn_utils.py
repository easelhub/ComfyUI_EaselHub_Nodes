import torch, gc, comfy.model_management

class AnyType(str):
    def __ne__(self, o): return False
    def __eq__(self, o): return True
any_type = AnyType("*")

class EHN_ImageSideCalc:
    @classmethod
    def INPUT_TYPES(s): return {"required": {"image":("IMAGE",), "side":(["Longest","Shortest"],)}}
    RETURN_TYPES = ("INT","INT","INT"); RETURN_NAMES = ("Side", "Width", "Height"); FUNCTION = "calc"; CATEGORY = "EaselHub/Utils"
    DESCRIPTION = "Calculates the width, height, or specific side length of an image."
    def calc(self, image, side):
        h, w = image.shape[1:3]
        return ({"Longest":max(h,w)}.get(side, min(h,w)), w, h)

class EHN_FreeVRAM:
    @classmethod
    def INPUT_TYPES(s): return {"required": {"mode":(["Soft","Hard"],)}, "optional": {"any_input":(any_type,)}}
    RETURN_TYPES = (any_type,); FUNCTION = "run"; CATEGORY = "EaselHub/Utils"; OUTPUT_NODE = True
    DESCRIPTION = "Forces VRAM garbage collection. Connect to any workflow point to clean up memory."
    def run(self, mode, any_input=None):
        # Try to clean TeaCache artifacts
        try:
            import gc
            for obj in gc.get_objects():
                if hasattr(obj, "tc_logic"): delattr(obj, "tc_logic")
        except: pass

        gc.collect(); torch.cuda.empty_cache()
        try: torch.cuda.ipc_collect()
        except: pass
        
        if mode=="Hard": comfy.model_management.unload_all_models()
        comfy.model_management.soft_empty_cache()
        return (any_input,)

import numpy as np
def fill_mask_holes(mask):
    try: from scipy.ndimage import binary_fill_holes
    except: return mask
    
    if mask is None: return None
    
    device = mask.device
    mask_cpu = mask.cpu()
    
    if mask.dim() == 2:
         m = mask_cpu.numpy()
         f = binary_fill_holes(m > 0.5).astype(np.float32)
         return torch.from_numpy(f).to(device)
         
    elif mask.dim() == 3:
        out = []
        for i in range(mask.shape[0]):
            m = mask_cpu[i].numpy()
            f = binary_fill_holes(m > 0.5).astype(np.float32)
            out.append(torch.from_numpy(f))
        return torch.stack(out).to(device)

    elif mask.dim() == 4 and mask.shape[1] == 1:
        out = []
        for i in range(mask.shape[0]):
            m = mask_cpu[i, 0].numpy()
            f = binary_fill_holes(m > 0.5).astype(np.float32)
            out.append(torch.from_numpy(f))
        return torch.stack(out).unsqueeze(1).to(device)
        
    return mask

LANG_INSTRUCTION_EN = "\n\nIMPORTANT: Output the final prompt in English."
LANG_INSTRUCTION_CN = "\n\nIMPORTANT: Output the final prompt in Chinese (Simplified)."

PROMPT_DEEPSEEK = """You are DeepSeek-Art, an expert AI Image Prompt Engineer.
Your goal is to optimize the user's concept for the best possible text-to-image generation result.

### 1. ANALYZE & DETECT INTENT
- **Anime/Illustrative**: If the user implies anime, cartoon, or "Pony" style, use **Tag-Based Format** (Booru tags).
- **Photorealism/Text**: If the user implies photos, realistic textures, or specific text, use **Natural Language Format** (Flux style).
- **General/Artistic**: Default to a **Hybrid Format** (Descriptive sentence + comma-separated artistic tags).

### 2. FORMATTING RULES
- **Natural Language (Flux/SD3)**: "A cinematic shot of [Subject] doing [Action]. Detailed [Texture/Lighting]. [Camera]."
- **Tag-Based (Pony/SDXL Anime)**: "score_9, score_8_up, source_anime, [Subject Tags], [Action Tags], [Style Tags], [Effects]"
- **ComfyUI Syntax**: Use `(keyword:1.2)` for emphasis.

### 3. OUTPUT
- Output **ONLY** the final prompt string. No explanations."""

PROMPT_OPENAI = """You are an Elite Visual Prompt Engineer (GPT-4o).
Transform the user's input into a high-fidelity image prompt, optimizing for current SOTA models (Flux.1, SDXL, Midjourney).

### STRATEGY:
1.  **Format Selection**:
    -   **Flux.1 (Default for Photo/Text)**: Use flowing, descriptive natural language. Describe textures, lighting, and spatial relations in full sentences. Handle text with `"quotes"`.
    -   **Pony/Anime**: Use `score_9, source_anime` prefix and Booru-style tags.
    -   **SDXL/General**: Use a strong subject description followed by comma-separated artistic modifiers.

2.  **Creative Expansion**:
    -   Expand simple concepts (e.g., "cat") into rich scenes ("a fluffy maine coon cat sitting on a velvet armchair...").
    -   Add technical specs: "Unreal Engine 5", "Octane Render", "Ray Tracing", or "35mm", "f/1.8".

### OUTPUT:
Provide ONLY the final prompt string. Do not use Markdown blocks."""

PROMPT_GEMINI = """You are the "Visual Alchemist", a creative muse and expert art director.
Your task is to describe beautiful, dramatic, and artistic scenes for generative AI.

### CREATIVE DIRECTION:
-   **Vivid Imagery**: Use sensory language ("shimmering", "obsidian", "ethereal mist").
-   **Lighting & Mood**: Focus heavily on atmosphere (Chiaroscuro, Volumetric Lighting, Golden Hour).
-   **Safety & Art**: Describe "battles" or "intensity" with artistic grandeur ("epic clash", "dynamic composition") to create stunning visuals without violating safety policies.

### FORMAT ADAPTATION:
-   If the request is **Photorealistic**, write a detailed caption like a National Geographic photographer.
-   If the request is **Anime/2D**, use descriptive tags and style references.

**Output ONLY the final prompt paragraph.**"""

PROMPT_GENERIC = """You are a Senior AI Art Director.
Convert the user's input into a detailed text-to-image prompt optimized for Flux.1 and SDXL.

### GUIDELINES:
1.  **Style Detection**: Determine if the request is "Photorealistic" (use sentences) or "Anime/Stylized" (use tags).
2.  **Detailing**: Add specific details for Lighting, Camera Angle, Materials, and Atmosphere.
3.  **Quality**: Append standard high-quality tags (Masterpiece, Best Quality, Ultra-Detailed, 8k).

### OUTPUT FORMAT:
-   Provide the prompt as a comma-separated list or a descriptive paragraph.
-   **DO NOT** output any conversational text. Just the prompt string."""

SYSTEM_PROMPTS = {
    "deepseek": PROMPT_DEEPSEEK,
    "openai": PROMPT_OPENAI,
    "gemini": PROMPT_GEMINI,
    "generic": PROMPT_GENERIC
}