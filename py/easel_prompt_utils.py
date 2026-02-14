import re, os

class Easel_PromptProcess:
    CATEGORY, RETURN_TYPES, RETURN_NAMES, FUNCTION = "EaselHub/Prompt", ("STRING",), ("prompt",), "run"
    @classmethod
    def INPUT_TYPES(s):
        bd = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        fs = ["None"] + [f for f in os.listdir(bd) if f.endswith('.txt') and f != "requirements.txt"] if os.path.exists(bd) else ["None"]
        return {"required": {"prompt": ("STRING", {"multiline": True, "forceInput": True})}, "optional": {"concat": ("STRING", {"multiline": True, "forceInput": True}), "sep": ("STRING", {"default": ","}), "file": (sorted(fs), {"default": "None"}), "pairs": ("STRING", {"multiline": True, "default": ""})}}
    def run(self, prompt, concat="", sep=",", file="None", pairs=""):
        p = f"{prompt}{sep}{concat}" if concat else prompt
        reps = []
        if file != "None":
            fp = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), file)
            if os.path.exists(fp):
                with open(fp, 'r', encoding='utf-8') as f: reps.extend([l.strip().split('|', 1) for l in f if '|' in l])
        if pairs: reps.extend([l.strip().split('|', 1) for l in pairs.split('\n') if '|' in l])
        for k, v in reps: p = re.sub(re.escape(k), v, p, flags=re.IGNORECASE)
        return (re.sub(r'\b(\w+)(?:\s+\1\b)+', r'\1', p, flags=re.IGNORECASE),)
