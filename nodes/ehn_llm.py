import requests, json, os
from .ehn_utils import SYSTEM_PROMPTS, LANG_INSTRUCTION_CN, LANG_INSTRUCTION_EN

def load_llm_json():
    try:
        p = os.path.join(os.path.dirname(os.path.dirname(__file__)), "web", "ehn_llm.json")
        if os.path.exists(p):
            with open(p, 'r', encoding='utf-8') as f: return json.load(f)
    except: pass
    return {}

MODELS = load_llm_json()

def fetch_and_update_models(provider, api_key, base_url=None):
    try:
        new_list = []
        if provider == "openai":
            url = (base_url or "https://api.openai.com/v1").rstrip("/") + "/models"
            r = requests.get(url, headers={"Authorization": f"Bearer {api_key}"}, timeout=10)
            r.raise_for_status()
            # Filter for likely chat models, excluding audio/embedding/legacy
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
            # Check supportedGenerationMethods for 'generateContent'
            new_list = sorted([m["name"].split("/")[-1] for m in r.json().get("models", []) 
                             if "gemini" in m["name"].lower() and "generateContent" in m.get("supportedGenerationMethods", [])])
        elif provider == "siliconflow":
            # 1. Get authoritative list from API
            all_models = []
            try:
                r = requests.get("https://api.siliconflow.cn/v1/models", headers={"Authorization": f"Bearer {api_key}"}, timeout=10)
                if r.status_code == 200:
                    all_models = set([m["id"] for m in r.json()["data"]])
            except: pass

            # 2. Try to get free/cheap models from web listing (sorted by price)
            # URL provided by user suggests this endpoint/page exists and sorts by price.
            # We fetch a large page to cover free models.
            try:
                web_url = "https://siliconflow.cn/models?order=price&orderBy=asc&pageSize=30"
                # Add headers to mimic browser
                h = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
                r = requests.get(web_url, headers=h, timeout=10)
                
                found_ids = []
                if r.status_code == 200:
                    # If it returns JSON (API backing the page)
                    try:
                        data = r.json()
                        # Assuming data structure contains a list under 'data' or 'models' or root
                        items = data.get("data", data.get("models", data if isinstance(data, list) else []))
                        for item in items:
                            if isinstance(item, dict):
                                mid = item.get("id", item.get("name"))
                                # Verify this is a real model ID (exists in API list)
                                if mid and (not all_models or mid in all_models):
                                    found_ids.append(mid)
                    except:
                        # Fallback: regex search for model IDs in HTML
                        import re
                        # Look for strings that look like model IDs (Vendor/Model)
                        # and are present in our authoritative list
                        candidates = re.findall(r'["\']([\w\-\./]+)["\']', r.text)
                        for c in candidates:
                            if c in all_models and c not in found_ids:
                                found_ids.append(c)
                
                if found_ids:
                    new_list = sorted(found_ids)
            except: pass
            
            # 3. Fallback if web fetch failed but we have API list:
            # Filter by known free model families if we couldn't determine price
            if not new_list and all_models:
                # Heuristic: DeepSeek V3/R1 and Qwen 2.5 are often free/cheap on SiliconFlow
                new_list = sorted([m for m in all_models if "DeepSeek-V3" in m or "DeepSeek-R1" in m or "Qwen/Qwen2.5" in m or "glm-4-9b" in m])
        elif provider == "openrouter":
            # Try official API first
            try:
                r = requests.get("https://openrouter.ai/api/v1/models", timeout=10)
                r.raise_for_status()
                data = r.json()["data"]
                # Filter for free models: prompt and completion pricing are 0
                new_list = sorted([m["id"] for m in data 
                                 if float(m.get("pricing", {}).get("prompt", 0)) == 0 
                                 and float(m.get("pricing", {}).get("completion", 0)) == 0])
            except:
                # Fallback to scraping user provided URL if API fails (simulated) or just return empty
                # Since scraping html is unreliable without heavy deps, we try another endpoint if exists or return empty.
                pass
        
        if new_list:
            p = os.path.join(os.path.dirname(os.path.dirname(__file__)), "web", "ehn_llm.json")
            data = {}
            if os.path.exists(p):
                with open(p, 'r', encoding='utf-8') as f: data = json.load(f)
            data[provider] = new_list
            with open(p, 'w', encoding='utf-8') as f: json.dump(data, f, indent=4)
            return new_list
    except Exception as e:
        print(f"[EHN] Model fetch error: {e}")
        return []
    return []

class EHN_LLM_Base:
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("generated_text",)
    FUNCTION = "generate_prompt"
    CATEGORY = "EaselHub/Generation"
    
    @staticmethod
    def _types(models, key_def="sk-...", extra=None, default_sys_prompt=SYSTEM_PROMPTS["generic"]):
        req = {"api_key":("STRING",{"default":key_def}), "model":models, "system_prompt":("STRING",{"multiline":True,"default":default_sys_prompt}), "user_prompt":("STRING",{"multiline":True,"default":"..."})}
        opt = {"language":(["English","Chinese"],), "seed":("INT",{"default":0}), "timeout":("INT",{"default":60, "min":1, "max":300})}
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
    def INPUT_TYPES(s):
        return {
            "required": {
                "api_key": ("STRING", {"default": "sk-..."}),
                "model": (MODELS.get("siliconflow", ["deepseek-ai/DeepSeek-R1-0528-Qwen3-8B", "Qwen/Qwen3-8B"]),),
                "custom_model_name": ("STRING", {"default": ""}),
                "system_prompt": ("STRING", {"multiline": True, "default": SYSTEM_PROMPTS["generic"]}),
                "user_prompt": ("STRING", {"multiline": True, "default": "..."})
            },
            "optional": {
                "language": (["English", "Chinese"],),
                "seed": ("INT", {"default": 0}),
                "timeout": ("INT", {"default": 60, "min": 1, "max": 300})
            }
        }
    DESCRIPTION = "Generates prompts using SiliconFlow API."
    def generate_prompt(self, api_key, model, user_prompt, system_prompt, seed, language="English", custom_model_name="", timeout=60):
        return self._exec("https://api.siliconflow.cn/v1/chat/completions", api_key, custom_model_name or model, user_prompt, system_prompt, language, seed, timeout)

class EHN_OpenRouter(EHN_LLM_Base):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "api_key": ("STRING", {"default": "sk-or-..."}),
                "model": (MODELS.get("openrouter", ["deepseek/deepseek-r1-0528:free", "google/gemma-3-27b-it:free"]),),
                "custom_model_name": ("STRING", {"default": ""}),
                "system_prompt": ("STRING", {"multiline": True, "default": SYSTEM_PROMPTS["generic"]}),
                "user_prompt": ("STRING", {"multiline": True, "default": "..."})
            },
            "optional": {
                "language": (["English", "Chinese"],),
                "seed": ("INT", {"default": 0}),
                "timeout": ("INT", {"default": 60, "min": 1, "max": 300})
            }
        }
    DESCRIPTION = "Generates prompts using OpenRouter API."
    def generate_prompt(self, api_key, model, user_prompt, system_prompt, seed, language="English", custom_model_name="", timeout=60):
        p = {"model": custom_model_name or model, "messages": [{"role":"system","content":system_prompt + (LANG_INSTRUCTION_CN if language=="Chinese" else LANG_INSTRUCTION_EN)}, {"role":"user","content":user_prompt}], "provider":{"order":["DeepSeek","Together"],"allow_fallbacks":True}}
        return self._exec("https://openrouter.ai/api/v1/chat/completions", api_key, "", "", "", "", seed, timeout, {"HTTP-Referer":"https://github.com","X-Title":"EaselHub"}, p)

class EHN_DeepSeek(EHN_LLM_Base):
    @classmethod
    def INPUT_TYPES(s): return s._types((MODELS.get("deepseek", ["deepseek-chat", "deepseek-reasoner"]),), default_sys_prompt=SYSTEM_PROMPTS["deepseek"])
    DESCRIPTION = "Generates prompts using DeepSeek official API."
    def generate_prompt(self, api_key, model, user_prompt, system_prompt, seed, language="English", timeout=60):
        return self._exec("https://api.deepseek.com/chat/completions", api_key, model, user_prompt, system_prompt, language, seed, timeout)

class EHN_OpenAI(EHN_LLM_Base):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "base_url": ("STRING", {"default": "https://api.openai.com/v1"}),
                "api_key": ("STRING", {"default": "sk-..."}),
                "model": (MODELS.get("openai", ["gpt-4o", "gpt-4o-mini"]),),
                "system_prompt": ("STRING", {"multiline": True, "default": SYSTEM_PROMPTS["openai"]}),
                "user_prompt": ("STRING", {"multiline": True, "default": "..."})
            },
            "optional": {
                "language": (["English", "Chinese"],),
                "seed": ("INT", {"default": 0}),
                "timeout": ("INT", {"default": 60, "min": 1, "max": 300})
            }
        }
    DESCRIPTION = "Generates prompts using OpenAI API."
    def generate_prompt(self, base_url, api_key, model, user_prompt, system_prompt, seed, language="English", timeout=60):
        u = base_url.rstrip("/") + ("/chat/completions" if not base_url.endswith("/chat/completions") else "")
        return self._exec(u, api_key, model, user_prompt, system_prompt, language, seed, timeout)

class EHN_Gemini(EHN_LLM_Base):
    @classmethod
    def INPUT_TYPES(s): return s._types((MODELS.get("gemini", ["gemini-2.0-flash", "gemini-1.5-pro"]),), "AIza...", default_sys_prompt=SYSTEM_PROMPTS["gemini"])
    DESCRIPTION = "Generates prompts using Google Gemini API."
    def generate_prompt(self, api_key, model, user_prompt, system_prompt, seed, language="English", timeout=60):
        sys = system_prompt + (LANG_INSTRUCTION_CN if language=="Chinese" else LANG_INSTRUCTION_EN)
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        payload = {"contents": [{"parts": [{"text": sys + "\n\n" + user_prompt}]}], "generationConfig": {"temperature": 0.7}}
        try:
            r = requests.post(url, headers={"Content-Type":"application/json"}, json=payload, timeout=timeout)
            d = r.json()
            return (d.get("candidates",[{}])[0].get("content",{}).get("parts",[{}])[0].get("text","Error"),)
        except Exception as e: return (str(e),)

class EHN_CustomLLM(EHN_LLM_Base):
    @classmethod
    def INPUT_TYPES(s): return {"required":{"base_url":("STRING",{"default":"http://localhost:11434/v1"}), "api_key":("STRING",{"default":"sk-..."}), "model":("STRING",{"default":"llama3"}), "system_prompt":("STRING",{"multiline":True,"default":SYSTEM_PROMPTS["generic"]}), "user_prompt":("STRING",{"multiline":True})}, "optional":{"language":(["English","Chinese"],), "seed":("INT",{"default":0}), "timeout":("INT",{"default":60, "min":1, "max":300})}}
    DESCRIPTION = "Connects to a local or custom OpenAI-compatible LLM endpoint (e.g., Ollama)."
    def generate_prompt(self, base_url, api_key, model, user_prompt, system_prompt, seed, language="English", timeout=60):
        u = base_url.rstrip("/") + ("/chat/completions" if not base_url.endswith("/chat/completions") else "")
        return self._exec(u, "ollama" if api_key=="sk-..." else api_key, model, user_prompt, system_prompt, language, seed, timeout)