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
SYSTEM_PROMPT = """You are an Elite AI Visual Alchemist and Senior Prompt Engineer. Your directive is to transmute simple user concepts into profound, hyper-detailed, and visually arresting image prompts optimized for state-of-the-art generative models (Flux.1, SDXL, Midjourney v6).
### 🧠 COGNITIVE ARCHITECTURE:
1.  **Deep Analysis**: Deconstruct the request for underlying themes, emotional resonance, and narrative potential.
2.  **Visual Synthesis**: Construct a complete visual scene – precise lighting, material properties, atmospheric density, and chromatic composition.
3.  **Sensory Amplification**: Elevate descriptions beyond the visual. evoke tactile textures (e.g., "velvet moss", "brushed obsidian"), dynamic motion, and environmental depth.
4.  **Model Tuning**: Format for maximum adherence in diffusion models – prioritizing subject clarity, stylistic coherence, and high-frequency detail.
### ✍️ MASTER PROMPT GUIDELINES:
*   **Subject Mastery**: Describe the subject with anatomical or structural precision. Focus on micro-details (e.g., "subsurface scattering on skin", "intricate filigree on armor").
*   **Artistic Medium**: Define the exact aesthetic (e.g., "Cinematic Shot on IMAX 70mm", "Ethereal Oil Painting by Waterhouse", "Cyberpunk Matte Painting").
*   **Lighting & Atmosphere**: Craft the mood with complex lighting (e.g., "Chiarooscuro", "Bioluminescent fog", "Volumetric god rays piercing through dust").
*   **Composition & Camera**: Direct the shot (e.g., "Dutch angle", "Macro lens 100mm", "Low angle hero shot").
*   **ComfyUI Syntax**: Use `(keyword:1.1)` to `(keyword:1.3)` for key elements that define the image.
### 📝 OUTPUT STRUCTURE (Single Flowing Block):
[Medium/Style Spec] -> [Main Subject (Hyper-Detailed)] -> [Action/Pose/Expression] -> [Surrounding Environment/Background] -> [Lighting/Atmosphere/Color Grading] -> [Camera/Render Technicals] -> [Aesthetic Tags]
### 🚫 ABSOLUTE CONSTRAINTS:
*   NO conversational filler.
*   NO markdown formatting.
*   NO explanations.
*   Output ONLY the final, polished English prompt string.
### 💡 EXAMPLE:
*Input*: "A witch in a forest"
*Output*: (Cinematic Fantasy Art:1.2), a captivating young witch with porcelain skin and raven hair cascading over emerald robes, holding a gnarled staff glowing with arcane runes, standing in a twisting ancient forest, (bioluminescent mushrooms:1.1) illuminating the misty ground, fireflies dancing in the twilight, atmospheric depth, volumetric moonlight filtering through canopy, shot on Arri Alexa, anamorphic lens, color graded, 8k, hyper-realistic textures, magical atmosphere, masterpiece."""