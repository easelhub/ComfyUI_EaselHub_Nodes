import random
import os
import re

class EHN_PromptList:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "dynamicPrompts": False}),
                "delimiter": ("STRING", {"default": "\\n"}),
                "action": (["sequential", "shuffle", "random_pick", "pick_by_index"],),
                "start_index": ("INT", {"default": 0, "min": 0}),
                "limit_count": ("INT", {"default": 0, "min": 0}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            }
        }
    RETURN_TYPES = ("STRING",)
    OUTPUT_IS_LIST = (True,)
    FUNCTION = "run"
    CATEGORY = "EaselHub Nodes/Text"
    def run(self, text, delimiter, action, start_index, limit_count, seed):
        if not delimiter: data = [text.strip()]
        else:
            sep = delimiter.replace("\\n", "\n").replace("\\r", "\r").replace("\\t", "\t")
            data = [x.strip() for x in text.split(sep) if x.strip()]
        if not data: return ([""],)
        count = len(data)
        if action == "pick_by_index":
            return ([data[start_index % count]],)
        if action == "random_pick":
            rng = random.Random(seed)
            num = limit_count if limit_count > 0 else 1
            return ([rng.choice(data) for _ in range(num)],)
        if action == "shuffle":
            random.Random(seed).shuffle(data)
        start = start_index % count
        res = data[start:] + data[:start]
        if limit_count > 0: res = res[:limit_count]
        return (res,)

class EHN_PromptMix:
    @classmethod
    def INPUT_TYPES(s):
        d = os.path.join(os.path.dirname(os.path.dirname(__file__)), "txt")
        f = [x for x in os.listdir(d) if x.endswith(".txt")] if os.path.exists(d) else []
        return {
            "required": {
                "text_a": ("STRING", {"forceInput": True}),
                "separator": ("STRING", {"default": ","}),
                "preset": (["None"] + f,),
            },
            "optional": {
                "text_b": ("STRING", {"forceInput": True}),
                "replace_rules": ("STRING", {"multiline": True, "default": ""}),
            }
        }
    RETURN_TYPES = ("STRING",)
    FUNCTION = "run"
    CATEGORY = "EaselHub Nodes/Text"
    def run(self, text_a, separator, preset, text_b="", replace_rules=""):
        parts = [x for x in [text_a, text_b] if x]
        res = f"{separator} ".join(parts)
        rules = replace_rules.splitlines()
        if preset != "None":
            p = os.path.join(os.path.dirname(os.path.dirname(__file__)), "txt", preset)
            if os.path.exists(p):
                with open(p, "r", encoding="utf-8") as f: rules.extend(f.read().splitlines())
        for line in rules:
            if "|" in line:
                k, v = line.split("|", 1)
                res = res.replace(k, v)
        res = re.sub(r'\s+', ' ', res).strip()
        res = re.sub(r'([,.?!;:])\1+', r'\1', res)
        return (re.sub(r'\s*([,.?!;:])\s*', r'\1 ', res).strip(),)