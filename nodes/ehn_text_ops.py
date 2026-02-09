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
