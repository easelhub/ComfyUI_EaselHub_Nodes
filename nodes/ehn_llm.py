import requests, json
from .ehn_utils import SYSTEM_PROMPT, LANG_INSTRUCTION_CN, LANG_INSTRUCTION_EN

class EHN_LLM_Base:
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("generated_text",)
    FUNCTION = "generate_prompt"
    CATEGORY = "EaselHub/Generation"
    
    @staticmethod
    def _types(models, key_def="sk-...", extra=None):
        req = {"api_key":("STRING",{"default":key_def}), "model":models, "system_prompt":("STRING",{"multiline":True,"default":SYSTEM_PROMPT}), "user_prompt":("STRING",{"multiline":True,"default":"..."})}
        opt = {"custom_model_name":("STRING",{"default":""}), "language":(["English","Chinese"],), "seed":("INT",{"default":0}), "timeout":("INT",{"default":60, "min":1, "max":300})}
        if extra: opt.update(extra)
        return {"required": req, "optional": opt}

    def _exec(self, url, key, model, usr, sys, lang, seed, timeout=60, headers=None, payload=None, method="post"):
        if not key or "..." in key: return ("Invalid API Key",)
        sys += LANG_INSTRUCTION_CN if lang == "Chinese" else LANG_INSTRUCTION_EN
        h = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        if headers: h.update(headers)
        p = {"model": model, "messages": [{"role":"system","content":sys}, {"role":"user","content":usr}], "temperature": 0.7}
        if seed is not None: p["seed"] = seed
        if payload: p = payload
        try:
            r = requests.post(url, headers=h, json=p, timeout=timeout) if method=="post" else requests.get(url, headers=h, params=p, timeout=timeout)
            r.raise_for_status()
            d = r.json()
            if "choices" in d: return (d["choices"][0]["message"]["content"],)
            if "candidates" in d: return (d["candidates"][0]["content"]["parts"][0]["text"],)
            return (f"Err: {json.dumps(d)}",)
        except Exception as e: return (f"API Error: {e}",)

class EHN_SiliconFlow(EHN_LLM_Base):
    @classmethod
    def INPUT_TYPES(s): return s._types((["deepseek-ai/DeepSeek-R1-0528-Qwen3-8B", "Qwen/Qwen3-8B", "THUDM/glm-4-9b-chat", "tencent/Hunyuan-MT-7B"],))
    DESCRIPTION = "Generates prompts using SiliconFlow API."
    def generate_prompt(self, api_key, model, user_prompt, system_prompt, seed, custom_model_name="", language="English", timeout=60):
        return self._exec("https://api.siliconflow.cn/v1/chat/completions", api_key, custom_model_name or model, user_prompt, system_prompt, language, seed, timeout)

class EHN_OpenRouter(EHN_LLM_Base):
    @classmethod
    def INPUT_TYPES(s): return s._types((["deepseek/deepseek-r1-0528:free", "qwen/qwen3-4b:free", "google/gemma-3-27b-it:free"],), "sk-or-...")
    DESCRIPTION = "Generates prompts using OpenRouter API."
    def generate_prompt(self, api_key, model, user_prompt, system_prompt, seed, custom_model_name="", language="English", timeout=60):
        p = {"model": custom_model_name or model, "messages": [{"role":"system","content":system_prompt + (LANG_INSTRUCTION_CN if language=="Chinese" else LANG_INSTRUCTION_EN)}, {"role":"user","content":user_prompt}], "provider":{"order":["DeepSeek","Together"],"allow_fallbacks":True}}
        return self._exec("https://openrouter.ai/api/v1/chat/completions", api_key, "", "", "", "", seed, timeout, {"HTTP-Referer":"https://github.com","X-Title":"EaselHub"}, p)

class EHN_DeepSeek(EHN_LLM_Base):
    @classmethod
    def INPUT_TYPES(s): return s._types((["deepseek-chat", "deepseek-reasoner"],))
    DESCRIPTION = "Generates prompts using DeepSeek official API."
    def generate_prompt(self, api_key, model, user_prompt, system_prompt, seed, custom_model_name="", language="English", timeout=60):
        return self._exec("https://api.deepseek.com/chat/completions", api_key, custom_model_name or model, user_prompt, system_prompt, language, seed, timeout)

class EHN_OpenAI(EHN_LLM_Base):
    @classmethod
    def INPUT_TYPES(s): return s._types((["gpt-4o", "gpt-4o-mini", "o1-mini"],), extra={"base_url":("STRING",{"default":"https://api.openai.com/v1"})})
    DESCRIPTION = "Generates prompts using OpenAI API."
    def generate_prompt(self, api_key, model, user_prompt, system_prompt, seed, custom_model_name="", language="English", base_url="https://api.openai.com/v1", timeout=60):
        u = base_url.rstrip("/") + ("/chat/completions" if not base_url.endswith("/chat/completions") else "")
        return self._exec(u, api_key, custom_model_name or model, user_prompt, system_prompt, language, seed, timeout)

class EHN_Gemini(EHN_LLM_Base):
    @classmethod
    def INPUT_TYPES(s): return s._types((["gemini-2.0-flash", "gemini-1.5-pro"],), "AIza...")
    DESCRIPTION = "Generates prompts using Google Gemini API."
    def generate_prompt(self, api_key, model, user_prompt, system_prompt, seed, custom_model_name="", language="English", timeout=60):
        m = custom_model_name or model
        sys = system_prompt + (LANG_INSTRUCTION_CN if language=="Chinese" else LANG_INSTRUCTION_EN)
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={api_key}"
        payload = {"contents": [{"parts": [{"text": sys + "\n\n" + user_prompt}]}], "generationConfig": {"temperature": 0.7}}
        try:
            r = requests.post(url, headers={"Content-Type":"application/json"}, json=payload, timeout=timeout)
            d = r.json()
            return (d.get("candidates",[{}])[0].get("content",{}).get("parts",[{}])[0].get("text","Error"),)
        except Exception as e: return (str(e),)

class EHN_CustomLLM(EHN_LLM_Base):
    @classmethod
    def INPUT_TYPES(s): return {"required":{"base_url":("STRING",{"default":"http://localhost:11434/v1"}), "api_key":("STRING",{"default":"sk-..."}), "model":("STRING",{"default":"llama3"}), "system_prompt":("STRING",{"multiline":True,"default":SYSTEM_PROMPT}), "user_prompt":("STRING",{"multiline":True})}, "optional":{"language":(["English","Chinese"],), "seed":("INT",{"default":0}), "timeout":("INT",{"default":60, "min":1, "max":300})}}
    DESCRIPTION = "Connects to a local or custom OpenAI-compatible LLM endpoint (e.g., Ollama)."
    def generate_prompt(self, base_url, api_key, model, user_prompt, system_prompt, seed, language="English", timeout=60):
        u = base_url.rstrip("/") + ("/chat/completions" if not base_url.endswith("/chat/completions") else "")
        return self._exec(u, "ollama" if api_key=="sk-..." else api_key, model, user_prompt, system_prompt, language, seed, timeout)