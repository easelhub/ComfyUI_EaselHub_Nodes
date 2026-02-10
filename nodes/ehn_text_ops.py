import random

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
        return {
            "required": {
                "text_a": ("STRING", {"forceInput": True}),
                "separator": ("STRING", {"default": ","}),
            },
            "optional": {
                "text_b": ("STRING", {"forceInput": True}),
                "replace_rules": ("STRING", {"multiline": True, "default": ""}),
            }
        }
    RETURN_TYPES = ("STRING",)
    FUNCTION = "run"
    CATEGORY = "EaselHub Nodes/Text"

    def run(self, text_a, separator, text_b="", replace_rules=""):
        result = text_a
        if text_b:
            result = f"{text_a}{separator} {text_b}" if text_a else text_b
        if replace_rules:
            for line in replace_rules.splitlines():
                if "|" in line:
                    find, replace = line.split("|", 1)
                    result = result.replace(find, replace)
        return (result,)
