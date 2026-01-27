from .ehn_utils import any_type
G_CACHE = {}

class EHN_SetVariable:
    @classmethod
    def INPUT_TYPES(s): return {"required": {"input_data": (any_type,), "var_name": ("STRING", {"default": "MyVar"})}, "hidden": {"unique_id": "UNIQUE_ID"}}
    RETURN_TYPES = (any_type,); FUNCTION = "set"; CATEGORY = "EaselHub/Logic"; OUTPUT_NODE = True
    def set(self, input_data, var_name, unique_id=None): G_CACHE[var_name.strip()] = input_data; return (input_data,)

class EHN_GetVariable:
    @classmethod
    def INPUT_TYPES(s): return {"required": {"var_name": (sorted(list(G_CACHE.keys())) or ["(No Vars Found)"],)}}
    @classmethod
    def VALIDATE_INPUTS(s, var_name): return True
    @classmethod
    def IS_CHANGED(s, var_name): return float("nan")
    RETURN_TYPES = (any_type,); FUNCTION = "get"; CATEGORY = "EaselHub/Logic"
    def get(self, var_name): return (G_CACHE.get(var_name.strip(), None),)