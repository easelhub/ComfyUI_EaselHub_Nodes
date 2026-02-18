import re, os

class EHN_PromptProcess:
    @classmethod
    def INPUT_TYPES(s):
        p = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        f = sorted([x for x in os.listdir(p) if x.endswith('.txt') and x != 'requirements.txt']) if os.path.exists(p) else []
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True, "forceInput": True}),
                "delimiter": ("STRING", {"default": ", "}),
            },
            "optional": {
                "text_to_add": ("STRING", {"multiline": True, "forceInput": True}),
                "pairs": ("STRING", {"multiline": True, "default": ""}),
                "preset_file": (["None"] + f, {"default": "None"}),
            }
        }
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompt",)
    FUNCTION = "execute"
    CATEGORY = "EaselHub/Prompt"

    def execute(self, prompt, delimiter, text_to_add="", pairs="", preset_file="None"):
        reps = []
        if preset_file != "None":
            fp = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), preset_file)
            if os.path.exists(fp):
                with open(fp, 'r', encoding='utf-8') as f:
                    reps.extend([l.strip().split('|', 1) for l in f if '|' in l and not l.strip().startswith('#')])
        
        if pairs:
            reps.extend([l.strip().split('|', 1) for l in pairs.split('\n') if '|' in l and not l.strip().startswith('#')])

        for k, v in reps:
            prompt = re.sub(re.escape(k.strip()), v.strip(), prompt, flags=re.IGNORECASE)

        if text_to_add:
            prompt = f"{prompt}{delimiter}{text_to_add}" if prompt else text_to_add
        
        return (re.sub(r'\b(\w+)(?:\s+\1\b)+', r'\1', prompt, flags=re.IGNORECASE),)
