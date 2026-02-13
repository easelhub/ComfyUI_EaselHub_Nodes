import re
import os

class EHN_PromptProcess:
    @classmethod
    def INPUT_TYPES(s):
        txt_files = ["None"]
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if os.path.exists(base_dir):
            txt_files += [f for f in os.listdir(base_dir) if f.endswith('.txt') and f != "requirements.txt"]
            
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True, "default": "", "forceInput": True}),
            },
            "optional": {
                "concat_prompt": ("STRING", {"multiline": True, "default": "", "forceInput": True}),
                "separator": ("STRING", {"multiline": False, "default": ","}),
                "replace_file": (sorted(txt_files), {"default": "None"}),
                "replace_pairs": ("STRING", {"multiline": True, "default": "", "placeholder": "old1|new1\nold2|new2"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompt",)
    FUNCTION = "execute"
    CATEGORY = "EaselHub/Prompt"

    def execute(self, prompt, concat_prompt="", separator=",", replace_file="None", replace_pairs=""):
        if concat_prompt:
            prompt = f"{prompt}{separator}{concat_prompt}"
        
        replacements = []
        
        if replace_file != "None":
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            file_path = os.path.join(base_dir, replace_file)
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if '|' in line:
                            replacements.append(line.strip().split('|', 1))

        if replace_pairs:
            for line in replace_pairs.split('\n'):
                if '|' in line:
                    replacements.append(line.strip().split('|', 1))
        
        for find, replace in replacements:
            pattern = re.compile(re.escape(find), re.IGNORECASE)
            prompt = pattern.sub(replace, prompt)
        
        prompt = re.sub(r'\b(\w+)(?:\s+\1\b)+', r'\1', prompt, flags=re.IGNORECASE)
        
        return (prompt,)
