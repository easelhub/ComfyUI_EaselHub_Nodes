from .ehn_utils import any_type
import os, random

class EHN_PromptList:
    @classmethod
    def INPUT_TYPES(s): return {"required": {"selection_mode": (["Concatenate All", "Pick Random One"],)}, "optional": {"incoming_list": (any_type,), "load_from_file": ("STRING", {}), "split_multiline": ("BOOLEAN", {"default": False}), "text": ("STRING", {"multiline": True, "dynamicPrompts": True})}}
    RETURN_TYPES = ("STRING", "STRING", "INT"); RETURN_NAMES = ("List", "String", "Count"); OUTPUT_IS_LIST = (True, False, False)
    FUNCTION = "run"; CATEGORY = "EaselHub/Logic"
    
    @classmethod
    def IS_CHANGED(s, selection_mode, **kwargs): return float("nan") if "Pick" in selection_mode else ""
    
    def run(self, selection_mode, incoming_list=None, load_from_file="", split_multiline=False, **kwargs):
        lst = []
        if incoming_list: lst.extend([str(x) for x in (incoming_list if isinstance(incoming_list, list) else [incoming_list]) if str(x).strip()])
        if load_from_file and os.path.isfile(load_from_file):
            try: 
                with open(load_from_file, 'r', encoding='utf-8') as f: lst.extend([l.strip() for l in f if l.strip()])
            except: pass
        for k, v in kwargs.items():
            if (k=="text" or k.startswith("prompt")) and isinstance(v, str) and v.strip():
                lst.extend([l.strip() for l in v.splitlines() if l.strip()] if split_multiline else [v.strip()])
        if not lst: lst = [""]
        out = [random.choice(lst)] if "Pick" in selection_mode else lst
        return (out, "\n".join(out), len(out))