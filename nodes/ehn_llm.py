import requests, json, os

LANG_INSTRUCTION_EN = "\n\nIMPORTANT: Output the final prompt in English."
LANG_INSTRUCTION_CN = "\n\nIMPORTANT: Output the final prompt in Chinese (Simplified)."
SYSTEM_PROMPTS = {
    "deepseek": """You are DeepSeek-Art. Goal: Optimize concept for T2I generation.
    1. Intent: Anime->Tags; Photo->Natural Lang; Art->Hybrid.
    2. Format: Flux/SD3->Natural; Pony->Tags(score_9...); General->Hybrid.
    3. Output: ONLY final prompt string.""",
    "openai": """You are GPT-4o Visual Prompt Engineer.
    1. Flux.1: Flowing natural language, describe texture/lighting.
    2. Pony: score_9, source_anime, booru tags.
    3. SDXL: Subject + artistic tags.
    Output ONLY final prompt.""",
    "gemini": """You are the Visual Alchemist.
    - Vivid imagery, atmosphere, lighting.
    - Photo: Nat Geo caption. Anime: Tags/Style.
    Output ONLY final prompt paragraph.""",
    "generic": """Senior AI Art Director.
    1. Style Detection. 2. Detail Lighting/Camera. 3. Quality Tags.
    Output ONLY the prompt string."""
}

def load_llm_json():
    try:
        p = os.path.join(os.path.dirname(os.path.dirname(__file__)), "web", "ehn_llm.json")
        if os.path.exists(p):
            with open(p, 'r', encoding='utf-8') as f: return json.load(f)
    except: pass
    return {}

def fetch_and_update_models(provider, api_key, base_url=None):
    try:
        new_list = []
        if provider == "openai":
            url = (base_url or "https://api.openai.com/v1").rstrip("/") + "/models"
            r = requests.get(url, headers={"Authorization": f"Bearer {api_key}"}, timeout=10)
            r.raise_for_status()
            new_list = sorted([m["id"] for m in r.json()["data"] 
                             if ("gpt" in m["id"] or "o1" in m["id"]) 
                             and not any(x in m["id"] for x in ["audio", "realtime", "embedding", "instruct", "dall-e", "tts", "whisper"])])
        elif provider == "deepseek":
            r = requests.get("https://api.deepseek.com/models", headers={"Authorization": f"Bearer {api_key}"}, timeout=10)
            r.raise_for_status()
            new_list = sorted([m["id"] for m in r.json()["data"]])
        elif provider == "gemini":
            r = requests.get(f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}", timeout=10)
            r.raise_for_status()
            new_list = sorted([m["name"].split("/")[-1] for m in r.json().get("models", []) 
                             if "gemini" in m["name"].lower() and "generateContent" in m.get("supportedGenerationMethods", [])])
        elif provider == "siliconflow":
            try:
                r = requests.get("https://api.siliconflow.cn/v1/models", headers={"Authorization": f"Bearer {api_key}"}, timeout=10)
                if r.status_code == 200: new_list = sorted([m["id"] for m in r.json()["data"]])
            except: pass
        elif provider == "openrouter":
            try:
                r = requests.get("https://openrouter.ai/api/v1/models", timeout=10)
                if r.status_code == 200:
                    new_list = sorted([m["id"] for m in r.json()["data"] 
                                     if float(m.get("pricing", {}).get("prompt", 0)) == 0 and float(m.get("pricing", {}).get("completion", 0)) == 0])
            except: pass
        
        if new_list:
            data = load_llm_json()
            data[provider] = new_list
            with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), "web", "ehn_llm.json"), 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            return new_list
    except: pass
    return []

class LLM_Base:
    CATEGORY = "EaselHub/LLM"
    FUNCTION = "gen"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompt",)
    
    def get_models(self, provider):
        return load_llm_json().get(provider, [])

    def call_api(self, provider, api_key, model, prompt, sys_prompt, base_url=None):
        try:
            msgs = [{"role": "system", "content": sys_prompt}, {"role": "user", "content": prompt}]
            if provider == "gemini":
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
                data = {"contents": [{"parts": [{"text": sys_prompt + "\n\n" + prompt}]}]}
                r = requests.post(url, json=data, timeout=60)
                return r.json()['candidates'][0]['content']['parts'][0]['text']
            
            url = (base_url or {
                "openai": "https://api.openai.com/v1",
                "deepseek": "https://api.deepseek.com",
                "siliconflow": "https://api.siliconflow.cn/v1",
                "openrouter": "https://openrouter.ai/api/v1"
            }.get(provider, "")).rstrip("/") + "/chat/completions"
            
            h = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            if provider == "openrouter":
                h["HTTP-Referer"] = "https://github.com/comfyui"; h["X-Title"] = "ComfyUI Node"
                
            data = {"model": model, "messages": msgs, "temperature": 0.7}
            r = requests.post(url, headers=h, json=data, timeout=60)
            return r.json()['choices'][0]['message']['content']
        except Exception as e: return f"Error: {str(e)}"

class EHN_SiliconFlow(LLM_Base):
    @classmethod
    def INPUT_TYPES(s): return {"required": {"api_key": ("STRING", {"multiline": False}), "model": (s().get_models("siliconflow") or ["Please Update Models"],), "prompt": ("STRING", {"multiline": True}), "language": (["English", "Chinese"],)}}
    def gen(self, api_key, model, prompt, language):
        return (self.call_api("siliconflow", api_key, model, prompt, SYSTEM_PROMPTS["deepseek"] + (LANG_INSTRUCTION_EN if language=="English" else LANG_INSTRUCTION_CN)),)

class EHN_OpenRouter(LLM_Base):
    @classmethod
    def INPUT_TYPES(s): return {"required": {"api_key": ("STRING", {"multiline": False}), "model": (s().get_models("openrouter") or ["Please Update Models"],), "prompt": ("STRING", {"multiline": True})}}
    def gen(self, api_key, model, prompt):
        return (self.call_api("openrouter", api_key, model, prompt, SYSTEM_PROMPTS["generic"] + LANG_INSTRUCTION_EN),)

class EHN_DeepSeek(LLM_Base):
    @classmethod
    def INPUT_TYPES(s): return {"required": {"api_key": ("STRING", {"multiline": False}), "model": (["deepseek-chat", "deepseek-reasoner"],), "prompt": ("STRING", {"multiline": True})}}
    def gen(self, api_key, model, prompt):
        return (self.call_api("deepseek", api_key, model, prompt, SYSTEM_PROMPTS["deepseek"] + LANG_INSTRUCTION_EN),)

class EHN_OpenAI(LLM_Base):
    @classmethod
    def INPUT_TYPES(s): return {"required": {"api_key": ("STRING", {"multiline": False}), "model": (s().get_models("openai") or ["gpt-4o", "gpt-3.5-turbo"],), "prompt": ("STRING", {"multiline": True})}}
    def gen(self, api_key, model, prompt):
        return (self.call_api("openai", api_key, model, prompt, SYSTEM_PROMPTS["openai"] + LANG_INSTRUCTION_EN),)

class EHN_Gemini(LLM_Base):
    @classmethod
    def INPUT_TYPES(s): return {"required": {"api_key": ("STRING", {"multiline": False}), "model": (s().get_models("gemini") or ["gemini-1.5-flash"],), "prompt": ("STRING", {"multiline": True})}}
    def gen(self, api_key, model, prompt):
        return (self.call_api("gemini", api_key, model, prompt, SYSTEM_PROMPTS["gemini"] + LANG_INSTRUCTION_EN),)

class EHN_CustomLLM(LLM_Base):
    @classmethod
    def INPUT_TYPES(s): return {"required": {"base_url": ("STRING", {"default": "http://localhost:1234/v1"}), "api_key": ("STRING", {"default": "lm-studio"}), "model": ("STRING", {"default": "local-model"}), "prompt": ("STRING", {"multiline": True})}}
    def gen(self, base_url, api_key, model, prompt):
        return (self.call_api("custom", api_key, model, prompt, SYSTEM_PROMPTS["generic"], base_url),)
