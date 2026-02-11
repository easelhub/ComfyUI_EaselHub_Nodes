import random
import os
import re

class EHN_PromptList:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "dynamicPrompts": False}),
                "split_lines": ("BOOLEAN", {"default": True}),
                "method": (["sequential", "random", "reverse"],),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "start_index": ("INT", {"default": 0, "min": 0}),
                "max_count": ("INT", {"default": 0, "min": 0}),
            }
        }
    RETURN_TYPES = ("STRING",)
    OUTPUT_IS_LIST = (True,)
    FUNCTION = "run"
    CATEGORY = "EaselHub Nodes/Text"

    def run(self, text, split_lines, method, seed, start_index, max_count):
        lines = [line.strip() for line in text.splitlines() if line.strip()] if split_lines else [text]
        if method == "random": random.Random(seed).shuffle(lines)
        elif method == "reverse": lines.reverse()
        return (lines[start_index:start_index + max_count] if max_count > 0 else lines[start_index:],)

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
        result = text_a
        if text_b: result = f"{text_a}{separator} {text_b}" if text_a else text_b
        rules = replace_rules.splitlines()
        if preset != "None":
            p = os.path.join(os.path.dirname(os.path.dirname(__file__)), "txt", preset)
            if os.path.exists(p):
                with open(p, "r", encoding="utf-8") as f:
                    rules.extend(f.read().splitlines())
        for line in rules:
            if "|" in line:
                k, v = line.split("|", 1)
                result = result.replace(k, v)
        result = re.sub(r'\s+', ' ', result).strip()
        result = re.sub(r'([,.?!;:])\1+', r'\1', result)
        result = re.sub(r'\s*([,.?!;:])\s*', r'\1 ', result).strip()
        return (result,)