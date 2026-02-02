from .ehn_utils import any_type
G_CACHE = {}

class EHN_SetVariable:
    @classmethod
    def INPUT_TYPES(s): return {"required": {"input_data": (any_type,), "var_name": ("STRING", {"default": "MyVar"})}, "hidden": {"unique_id": "UNIQUE_ID"}}
    RETURN_TYPES = (any_type,)
    RETURN_NAMES = ("data",)
    FUNCTION = "set"
    CATEGORY = "EaselHub/Logic"
    OUTPUT_NODE = True
    def set(self, input_data, var_name, unique_id=None):
        name = var_name.strip()
        G_CACHE[name] = input_data
        return (input_data,)

class EHN_GetVariable:
    @classmethod
    def INPUT_TYPES(s):
        l = sorted(list(G_CACHE.keys()))
        return {
            "required": {"var_name": (l if l else ["(No Vars Found)"],)}
        }
    @classmethod
    def VALIDATE_INPUTS(s, var_name, **kwargs): return True
    @classmethod
    def IS_CHANGED(s, **kwargs): return float("nan")
    RETURN_TYPES = (any_type,)
    RETURN_NAMES = ("data",)
    FUNCTION = "get"
    CATEGORY = "EaselHub/Logic"
    def get(self, var_name):
        name = var_name.strip()
        if name not in G_CACHE:
            print(f"[EHN_GetVariable] Warning: Variable '{name}' not defined in this session yet.")
            return (None,)
        return (G_CACHE[name],)