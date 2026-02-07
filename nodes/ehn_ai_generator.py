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
SYSTEM_PROMPT_PATH = os.path.join(ROOT_DIR, "ai_studio_code.txt")

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

def get_system_prompt():
    if os.path.exists(SYSTEM_PROMPT_PATH):
        with open(SYSTEM_PROMPT_PATH, 'r', encoding='utf-8') as f:
            return f.read()
    return "You are a helpful AI assistant."

class EHN_AIGenerator:
    @classmethod
    def INPUT_TYPES(s):
        config = load_config()
        platforms = ["OpenAI", "Gemini", "DeepSeek", "Mistral", "Grok", "OpenRouter", "SiliconFlow", "TogetherAI", "Custom"]
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
                "base_url": ("STRING", {"multiline": False, "default": ""}),
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

    def generate(self, platform, api_key, base_url, custom_model, model, prompt, seed):
        config = load_config()
        
        if not api_key and platform in config:
            api_key = config[platform].get("api_key", "")
            
        if not api_key:
            return ("Error: API Key missing", "Error: API Key missing")

        if custom_model:
            model = custom_model

        system_prompt = get_system_prompt()
        
        full_prompt = f"{system_prompt}\n\nUser Request: {prompt}\n\n[IMPORTANT]\nProvide TWO outputs:\n1. English Prompt (Mode A/B/C as appropriate)\n2. Chinese Prompt (Translated/Adapted)\n\nFormat your response EXACTLY as follows:\n---ENGLISH START---\n[English Prompt Here]\n---ENGLISH END---\n---CHINESE START---\n[Chinese Prompt Here]\n---CHINESE END---\n\nDo NOT include '/imagine prompt:', any other text, explanations, or thoughts."
        
        result_text = ""
        try:
            if platform == "Gemini":
                result_text = self.call_gemini(api_key, model, full_prompt)
            elif platform in ["OpenAI", "DeepSeek", "Grok", "OpenRouter", "SiliconFlow", "Custom"]:
                api_base = "https://api.openai.com/v1"
                if platform == "DeepSeek": api_base = "https://api.deepseek.com"
                elif platform == "Grok": api_base = "https://api.x.ai/v1"
                elif platform == "OpenRouter": api_base = "https://openrouter.ai/api/v1"
                elif platform == "SiliconFlow": api_base = "https://api.siliconflow.cn/v1"
                elif platform == "Custom": api_base = base_url
                
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

@PromptServer.instance.routes.post("/ehn/update_models")
async def update_models_route(request):
    data = await request.json()
    platform = data.get("platform")
    api_key = data.get("api_key")
    base_url = data.get("base_url", "")
    custom_model = data.get("custom_model", "")
    
    config = load_config()
    
    if not api_key and platform in config:
        api_key = config[platform].get("api_key", "")
    
    if platform == "Custom" and not base_url and platform in config:
        base_url = config[platform].get("base_url", "")

    if not platform or (platform != "Custom" and not api_key):
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
            if platform == "DeepSeek": api_base = "https://api.deepseek.com"
            elif platform == "Mistral": api_base = "https://api.mistral.ai/v1"
            elif platform == "Grok": api_base = "https://api.x.ai/v1"
            elif platform == "OpenRouter": api_base = "https://openrouter.ai/api/v1"
            elif platform == "SiliconFlow": api_base = "https://api.siliconflow.cn/v1"
            elif platform == "TogetherAI": api_base = "https://api.together.xyz/v1"
            elif platform == "Custom": api_base = base_url
            
            url = f"{api_base}/models"
            req = urllib.request.Request(url, headers={'Authorization': f'Bearer {api_key}'})
            with urllib.request.urlopen(req) as response:
                resp_data = json.loads(response.read().decode('utf-8'))
                data_list = resp_data.get('data', [])
                
                if platform == "OpenAI":
                    models = [m['id'] for m in data_list if 'gpt-3.5' in m['id'] or 'gpt-4o-mini' in m['id']]
                elif platform == "DeepSeek":
                    models = [m['id'] for m in data_list if 'deepseek' in m['id']]
                elif platform == "Mistral":
                    models = [m['id'] for m in data_list if 'mistral' in m['id']]
                elif platform == "Grok":
                    models = [m['id'] for m in data_list if 'grok' in m['id']]
                elif platform == "OpenRouter":
                    models = [
                        m['id'] for m in data_list
                        if (str(m.get('pricing', {}).get('prompt', '1')) == '0' and str(m.get('pricing', {}).get('completion', '1')) == '0')
                        or ':free' in m['id']
                    ]
                elif platform == "SiliconFlow":
                    models = [m['id'] for m in data_list if 'free' in m['id'] or 'deepseek' in m['id']]
                elif platform == "TogetherAI":
                    models = [m['id'] for m in data_list if 'free' in m['id'] or 'meta' in m['id']]
                elif platform == "Custom":
                    models = [m['id'] for m in data_list]

        if platform not in config:
            config[platform] = {}
        config[platform]["api_key"] = api_key
        if platform == "Custom":
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
