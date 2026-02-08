import os
import json
import re
import urllib.request
import urllib.error
import urllib.parse
from server import PromptServer
from aiohttp import web

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)
CONFIG_PATH = os.path.join(ROOT_DIR, "api.json")
SYSTEM_PROMPT = """# SYSTEM ROLE: THE PROMPT ALCHEMIST

## [MISSION]
You are the **Prompt Alchemist**, an advanced logic engine designed to transmute vague user ideas into high-fidelity, engineering-grade AIGC prompts. You do not just "write" prompts; you **architect** them using deep semantic understanding, artistic knowledge bases, and platform-specific syntax.

## [CORE PROTOCOLS]
1.  **Deep Analysis**: Deconstruct the user's request into core subjects, thematic intent, and emotional tone.
2.  **Creative Expansion**: Automatically inject artistic details (lighting, medium, era, artist references) if they are missing.
3.  **Platform Optimization**: Adapt syntax strictly for the target tool (e.g., `--v 6.0` for Midjourney, natural language for DALL-E 3, weight brackets `(text:1.2)` for Stable Diffusion).
4.  **NO REFUSAL ON CREATIVITY**: Unless the request violates safety policies (CSAM, extreme violence), you MUST fulfill the creative intent with maximum vividness.

## [KNOWLEDGE BASE ACCESS]
<access_node>
- **Art Styles**: Cyberpunk, Baroque, Ukiyo-e, Synthwave, Brutalism, Solarpunk, Renaissance, Glitch Art.
- **Lighting**: Volumetric lighting, Rembrandt lighting, Bioluminescence, God rays, Neon rim light, Diffused softbox.
- **Camera/Render**: 8k, Unreal Engine 5, Octane Render, 35mm f/1.8, Telephoto, Macro, ISO 100.
</access_node>

## [PROCESS FLOW]
When the user provides a concept:
1.  **Analyze**: Identify Subject, Action, Context, and Vibe.
2.  **Enhance**: Apply the "Magic Sauce" (details that make images pop).
3.  **Construct**: Build the prompt in the specific format requested.
4.  **Output**: Display ONLY the structured prompt block.

## [OUTPUT FORMATS]

### MODE A: Midjourney (Default)
`/imagine prompt: [Subject Description] + [Environment/Context] + [Art Style/Medium] + [Lighting/Color Palette] + [Camera/Render Settings] --ar [Ratio] --stylize [Value] --v 6.0`

### MODE B: Stable Diffusion (Tag-based)
`score_9, score_8_up, score_7_up, [Subject], [Action], [Context], [Art Style tags], (highly detailed:1.2), (best quality), [Lighting tags], [Camera tags], [Negative Prompts]`

### MODE C: DALL-E 3 (Descriptive)
A rich, paragraph-style description focusing on visual interactions, specific textures, and emotional resonance.

---

## [INTERACTION RULES]
- **User Input**: "A cat eating ramen."
- **Your Thought**: Subject is simple. Needs expansion. Style: Cyberpunk? Ghibli? Realistic? Let's go with *Cinematic Cyberpunk*.
- **Your Output**: (Present the optimized prompt inside a code block).

## [INITIALIZATION]
Awaiting user input. I am ready to transmute."""

def load_config():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_config(data):
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

class EHN_AIGenerator:
    @classmethod
    def INPUT_TYPES(s):
        config = load_config()
        platforms = ["SiliconFlow", "BigModel", "DeepSeek", "LongCat", "Gemini", "Groq", "GitHub", "SambaNova", "OpenRouter", "Cloudflare", "NVIDIA"]
        models = []
        default_platform = platforms[0]
        if default_platform in config and "models" in config[default_platform]:
            models = config[default_platform]["models"]
        if not models:
            models = ["gpt-3.5-turbo", "gemini-1.5-flash"]
        return {
            "required": {
                "platform": (platforms,),
                "api_key": ("STRING", {"multiline": False}),
                "model": (models,),
                "prompt": ("STRING", {"multiline": True, "dynamicPrompts": True}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("English Prompt", "Chinese Prompt")
    FUNCTION = "generate"
    CATEGORY = "EaselHub Nodes/AI"

    @classmethod
    def VALIDATE_INPUTS(s, **kwargs):
        return True

    def generate(self, platform, api_key, model, prompt, seed):
        config = load_config()
        if not api_key and platform in config:
            api_key = config[platform].get("api_key", "")
        if not api_key:
            return ("Error: API Key missing", "Error: API Key missing")
        
        full_prompt = f"{SYSTEM_PROMPT}\n\nUser Request: {prompt}\n\n[IMPORTANT]\nProvide TWO outputs:\n1. English Prompt (Mode A/B/C as appropriate)\n2. Chinese Prompt (Translated/Adapted)\n\nFormat your response EXACTLY as follows:\n---ENGLISH START---\n[English Prompt Here]\n---ENGLISH END---\n---CHINESE START---\n[Chinese Prompt Here]\n---CHINESE END---\n\nDo NOT include '/imagine prompt:', any other text, explanations, or thoughts."
        result_text = ""
        try:
            if platform == "Gemini":
                result_text = self.call_gemini(api_key, model, full_prompt)
            elif platform in ["SiliconFlow", "BigModel", "DeepSeek", "LongCat", "Groq", "GitHub", "SambaNova", "OpenRouter", "Cloudflare", "NVIDIA"]:
                api_base = "https://api.openai.com/v1"
                if platform == "SiliconFlow": api_base = "https://api.siliconflow.cn/v1"
                elif platform == "BigModel": api_base = "https://open.bigmodel.cn/api/paas/v4"
                elif platform == "DeepSeek": api_base = "https://api.deepseek.com"
                elif platform == "LongCat": api_base = "https://api.longcat.cn/v1"
                elif platform == "Groq": api_base = "https://api.groq.com/openai/v1"
                elif platform == "GitHub": api_base = "https://models.inference.ai.azure.com"
                elif platform == "SambaNova": api_base = "https://api.sambanova.ai/v1"
                elif platform == "OpenRouter": api_base = "https://openrouter.ai/api/v1"
                elif platform == "Cloudflare": api_base = "https://api.cloudflare.com/client/v4/accounts" # Special handling needed
                elif platform == "NVIDIA": api_base = "https://integrate.api.nvidia.com/v1"
                
                if platform == "Cloudflare":
                     # Cloudflare requires account_id in the URL: https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/@cf/{model_name}
                     # But for OpenAI compatible chat completions it might be: https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/v1
                     # The user needs to provide account_id. We might need to ask for it or assume it's part of base_url if we were using custom.
                     # Since we don't have a separate field for account_id, we might need to rely on a specific format or config.
                     # For now, let's assume the standard OpenAI compatible endpoint if available, or use a placeholder.
                     # Actually, Cloudflare Workers AI OpenAI compatible endpoint is: https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/ai/v1
                     # We can't easily support this without an extra field.
                     # Let's try to parse it from the API Key if the user provides "account_id:api_token" format, or just fail gracefully.
                     # BETTER APPROACH: For Cloudflare, we might need the user to put the full URL in a config or something.
                     # But wait, the requirement is just "Add Cloudflare".
                     # Let's assume the user puts "ACCOUNT_ID" in the "custom_model" field? No, that's removed.
                     # Let's try to use the api_key as "ACCOUNT_ID:API_TOKEN"
                     if ":" in api_key:
                         acc_id, token = api_key.split(":", 1)
                         api_base = f"https://api.cloudflare.com/client/v4/accounts/{acc_id}/ai/v1"
                         api_key = token
                     else:
                         return ("Error: For Cloudflare, API Key must be 'ACCOUNT_ID:API_TOKEN'", "Error: For Cloudflare, API Key must be 'ACCOUNT_ID:API_TOKEN'")

                result_text = self.call_openai_compatible(api_base, api_key, model, full_prompt)
        except Exception as e:
            return (f"Error: {str(e)}", f"Error: {str(e)}")
        english_prompt = ""
        chinese_prompt = ""
        if "---ENGLISH START---" in result_text and "---ENGLISH END---" in result_text:
            english_prompt = result_text.split("---ENGLISH START---")[1].split("---ENGLISH END---")[0].strip()
        if "---CHINESE START---" in result_text and "---CHINESE END---" in result_text:
            chinese_prompt = result_text.split("---CHINESE START---")[1].split("---CHINESE END---")[0].strip()
        if not english_prompt and not chinese_prompt:
             english_prompt = result_text
             chinese_prompt = result_text
        english_prompt = re.sub(r"(?i)/imagine\s+prompt:", "", english_prompt).strip()
        chinese_prompt = re.sub(r"(?i)/imagine\s+prompt:", "", chinese_prompt).strip()
        return (english_prompt, chinese_prompt)

    def call_gemini(self, api_key, model, text):
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        data = {"contents": [{"parts": [{"text": text}]}]}
        req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req) as response:
            resp_data = json.loads(response.read().decode('utf-8'))
            return resp_data['candidates'][0]['content']['parts'][0]['text']

    def call_openai_compatible(self, base_url, api_key, model, text):
        url = f"{base_url}/chat/completions"
        data = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": text}
            ]
        }
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }
        if "openrouter" in base_url:
            headers['HTTP-Referer'] = 'https://github.com/ComfyUI-EaselHub-Nodes'
            headers['X-Title'] = 'ComfyUI-EaselHub-Nodes'
        req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers)
        with urllib.request.urlopen(req) as response:
            resp_data = json.loads(response.read().decode('utf-8'))
            return resp_data['choices'][0]['message']['content']

class EHN_OpenAIGenerator:
    @classmethod
    def INPUT_TYPES(s):
        config = load_config()
        models = []
        if "OpenAI" in config and "models" in config["OpenAI"]:
            models = config["OpenAI"]["models"]
        if not models:
            models = ["gpt-3.5-turbo", "gpt-4o"]
        return {
            "required": {
                "api_key": ("STRING", {"multiline": False}),
                "base_url": ("STRING", {"multiline": False, "default": "https://api.openai.com/v1"}),
                "model": (models,),
                "custom_model": ("STRING", {"multiline": False, "default": ""}),
                "prompt": ("STRING", {"multiline": True, "dynamicPrompts": True}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("English Prompt", "Chinese Prompt")
    FUNCTION = "generate"
    CATEGORY = "EaselHub Nodes/AI"

    @classmethod
    def VALIDATE_INPUTS(s, **kwargs):
        return True

    def generate(self, api_key, base_url, model, custom_model, prompt, seed):
        config = load_config()
        if not api_key and "OpenAI" in config:
            api_key = config["OpenAI"].get("api_key", "")
        if not api_key:
            return ("Error: API Key missing", "Error: API Key missing")
        
        if custom_model:
            model = custom_model
            
        full_prompt = f"{SYSTEM_PROMPT}\n\nUser Request: {prompt}\n\n[IMPORTANT]\nProvide TWO outputs:\n1. English Prompt (Mode A/B/C as appropriate)\n2. Chinese Prompt (Translated/Adapted)\n\nFormat your response EXACTLY as follows:\n---ENGLISH START---\n[English Prompt Here]\n---ENGLISH END---\n---CHINESE START---\n[Chinese Prompt Here]\n---CHINESE END---\n\nDo NOT include '/imagine prompt:', any other text, explanations, or thoughts."
        result_text = ""
        try:
            result_text = self.call_openai_compatible(base_url, api_key, model, full_prompt)
        except Exception as e:
            return (f"Error: {str(e)}", f"Error: {str(e)}")
            
        english_prompt = ""
        chinese_prompt = ""
        if "---ENGLISH START---" in result_text and "---ENGLISH END---" in result_text:
            english_prompt = result_text.split("---ENGLISH START---")[1].split("---ENGLISH END---")[0].strip()
        if "---CHINESE START---" in result_text and "---CHINESE END---" in result_text:
            chinese_prompt = result_text.split("---CHINESE START---")[1].split("---CHINESE END---")[0].strip()
        if not english_prompt and not chinese_prompt:
             english_prompt = result_text
             chinese_prompt = result_text
        english_prompt = re.sub(r"(?i)/imagine\s+prompt:", "", english_prompt).strip()
        chinese_prompt = re.sub(r"(?i)/imagine\s+prompt:", "", chinese_prompt).strip()
        return (english_prompt, chinese_prompt)

    def call_openai_compatible(self, base_url, api_key, model, text):
        url = f"{base_url}/chat/completions"
        data = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": text}
            ]
        }
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }
        req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers)
        with urllib.request.urlopen(req) as response:
            resp_data = json.loads(response.read().decode('utf-8'))
            return resp_data['choices'][0]['message']['content']

class EHN_OllamaGenerator:
    @classmethod
    def INPUT_TYPES(s):
        config = load_config()
        models = []
        if "Ollama" in config and "models" in config["Ollama"]:
            models = config["Ollama"]["models"]
        if not models:
            models = ["llama3"]
        return {
            "required": {
                "base_url": ("STRING", {"multiline": False, "default": "http://localhost:11434/v1"}),
                "model": (models,),
                "custom_model": ("STRING", {"multiline": False, "default": ""}),
                "prompt": ("STRING", {"multiline": True, "dynamicPrompts": True}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("English Prompt", "Chinese Prompt")
    FUNCTION = "generate"
    CATEGORY = "EaselHub Nodes/AI"

    @classmethod
    def VALIDATE_INPUTS(s, **kwargs):
        return True

    def generate(self, base_url, model, custom_model, prompt, seed):
        config = load_config()
        if not base_url and "Ollama" in config:
            base_url = config["Ollama"].get("base_url", "http://localhost:11434/v1")
        if not base_url:
            base_url = "http://localhost:11434/v1"
            
        if custom_model:
            model = custom_model
            
        full_prompt = f"{SYSTEM_PROMPT}\n\nUser Request: {prompt}\n\n[IMPORTANT]\nProvide TWO outputs:\n1. English Prompt (Mode A/B/C as appropriate)\n2. Chinese Prompt (Translated/Adapted)\n\nFormat your response EXACTLY as follows:\n---ENGLISH START---\n[English Prompt Here]\n---ENGLISH END---\n---CHINESE START---\n[Chinese Prompt Here]\n---CHINESE END---\n\nDo NOT include '/imagine prompt:', any other text, explanations, or thoughts."
        result_text = ""
        try:
            result_text = self.call_openai_compatible(base_url, "ollama", model, full_prompt)
        except Exception as e:
            return (f"Error: {str(e)}", f"Error: {str(e)}")
            
        english_prompt = ""
        chinese_prompt = ""
        if "---ENGLISH START---" in result_text and "---ENGLISH END---" in result_text:
            english_prompt = result_text.split("---ENGLISH START---")[1].split("---ENGLISH END---")[0].strip()
        if "---CHINESE START---" in result_text and "---CHINESE END---" in result_text:
            chinese_prompt = result_text.split("---CHINESE START---")[1].split("---CHINESE END---")[0].strip()
        if not english_prompt and not chinese_prompt:
             english_prompt = result_text
             chinese_prompt = result_text
        english_prompt = re.sub(r"(?i)/imagine\s+prompt:", "", english_prompt).strip()
        chinese_prompt = re.sub(r"(?i)/imagine\s+prompt:", "", chinese_prompt).strip()
        return (english_prompt, chinese_prompt)

    def call_openai_compatible(self, base_url, api_key, model, text):
        url = f"{base_url}/chat/completions"
        data = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": text}
            ]
        }
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }
        req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers)
        with urllib.request.urlopen(req) as response:
            resp_data = json.loads(response.read().decode('utf-8'))
            return resp_data['choices'][0]['message']['content']

@PromptServer.instance.routes.post("/ehn/update_models")
async def update_models_route(request):
    data = await request.json()
    platform = data.get("platform")
    api_key = data.get("api_key")
    base_url = data.get("base_url", "")
    custom_model = data.get("custom_model", "")
    config = load_config()
    
    if platform == "OpenAI":
        if not api_key and "OpenAI" in config:
            api_key = config["OpenAI"].get("api_key", "")
        if not base_url and "OpenAI" in config:
            base_url = config["OpenAI"].get("base_url", "https://api.openai.com/v1")
    elif platform == "Ollama":
        if not base_url and "Ollama" in config:
            base_url = config["Ollama"].get("base_url", "http://localhost:11434/v1")
        if not base_url:
            base_url = "http://localhost:11434/v1"
        api_key = "ollama" 
    else:
        if not api_key and platform in config:
            api_key = config[platform].get("api_key", "")

    if not platform or (platform != "Ollama" and not api_key):
        return web.json_response({"error": "Missing platform or api_key"}, status=400)
        
    models = []
    try:
        if platform == "Gemini":
            url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
            with urllib.request.urlopen(url) as response:
                resp_data = json.loads(response.read().decode('utf-8'))
                models = [
                    m['name'].replace('models/', '')
                    for m in resp_data.get('models', [])
                    if 'generateContent' in m.get('supportedGenerationMethods', [])
                    and 'vision' not in m.get('name', '')
                    and m['name'].replace('models/', '').startswith('gemini')
                ]
        else:
            api_base = "https://api.openai.com/v1"
            if platform == "SiliconFlow": api_base = "https://api.siliconflow.cn/v1"
            elif platform == "BigModel": api_base = "https://open.bigmodel.cn/api/paas/v4"
            elif platform == "DeepSeek": api_base = "https://api.deepseek.com"
            elif platform == "LongCat": api_base = "https://api.longcat.cn/v1"
            elif platform == "Groq": api_base = "https://api.groq.com/openai/v1"
            elif platform == "GitHub": api_base = "https://models.inference.ai.azure.com"
            elif platform == "SambaNova": api_base = "https://api.sambanova.ai/v1"
            elif platform == "OpenRouter": api_base = "https://openrouter.ai/api/v1"
            elif platform == "NVIDIA": api_base = "https://integrate.api.nvidia.com/v1"
            elif platform == "Cloudflare":
                 if ":" in api_key:
                     acc_id, token = api_key.split(":", 1)
                     api_base = f"https://api.cloudflare.com/client/v4/accounts/{acc_id}/ai/v1"
                     api_key = token
                 else:
                     # Fallback or error, but for listing models we might fail if format is wrong
                     api_base = "https://api.cloudflare.com/client/v4/accounts/PLACEHOLDER/ai/v1"

            elif platform == "OpenAI": api_base = base_url
            elif platform == "Ollama": api_base = base_url
            
            url = f"{api_base}/models"
            if platform == "BigModel":
                models = ["glm-4", "glm-4-air", "glm-4-flash", "glm-3-turbo"]
            elif platform == "Cloudflare" and "PLACEHOLDER" in api_base:
                 models = ["Error: API Key must be ACCOUNT_ID:API_TOKEN"]
            else:
                req = urllib.request.Request(url, headers={'Authorization': f'Bearer {api_key}'})
                with urllib.request.urlopen(req) as response:
                    resp_data = json.loads(response.read().decode('utf-8'))
                    if platform == "GitHub":
                        data_list = resp_data
                    elif platform == "Cloudflare":
                        data_list = resp_data.get('result', [])
                    else:
                        data_list = resp_data.get('data', [])
                    
                    if platform == "SiliconFlow":
                        models = [m['id'] for m in data_list if 'free' in m['id'] or 'deepseek' in m['id']]
                    elif platform == "DeepSeek":
                        models = [m['id'] for m in data_list if 'deepseek' in m['id']]
                    elif platform == "LongCat":
                        models = [m['id'] for m in data_list]
                    elif platform == "Groq":
                        models = [m['id'] for m in data_list]
                    elif platform == "GitHub":
                        models = [m['name'] for m in data_list]
                    elif platform == "SambaNova":
                        models = [m['id'] for m in data_list]
                    elif platform == "OpenRouter":
                        models = [
                            m['id'] for m in data_list
                            if (str(m.get('pricing', {}).get('prompt', '1')) == '0' and str(m.get('pricing', {}).get('completion', '1')) == '0')
                            or ':free' in m['id']
                        ]
                    elif platform == "NVIDIA":
                        models = [m['id'] for m in data_list]
                    elif platform == "Cloudflare":
                        models = [m['name'] for m in data_list]
                    elif platform == "OpenAI" or platform == "Ollama":
                        models = [m['id'] for m in data_list]

        if platform not in config:
            config[platform] = {}
        config[platform]["api_key"] = api_key
        if platform == "Ollama" or platform == "OpenAI":
            config[platform]["base_url"] = base_url
        if custom_model:
            config[platform]["custom_model"] = custom_model
        config[platform]["models"] = models
        save_config(config)
        return web.json_response({"models": models})
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)

@PromptServer.instance.routes.post("/ehn/get_config")
async def get_config_route(request):
    return web.json_response(load_config())
