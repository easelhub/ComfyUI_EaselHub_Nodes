import random
from .ehn_utils import any_type

# Global Cache
EHN_GLOBAL_CACHE = {}

class EHN_SetVariable:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "input_data": (any_type,),
                "var_name": ("STRING", {"default": "MyVar", "multiline": False}),
            },
            "hidden": {"unique_id": "UNIQUE_ID"},
        }
    RETURN_TYPES = (any_type,)
    RETURN_NAMES = ("data",)
    FUNCTION = "set_value"
    CATEGORY = "EaselHub/Logic"
    OUTPUT_NODE = True

    def set_value(self, input_data, var_name, unique_id=None):
        EHN_GLOBAL_CACHE[var_name.strip()] = input_data
        return (input_data,)

class EHN_GetVariable:
    @classmethod
    def INPUT_TYPES(s):
        return { "required": { "var_name": (["(No Vars Found)"],), } }
    
    @classmethod
    def IS_CHANGED(s, var_name):
        return float("nan") # Always check

    RETURN_TYPES = (any_type,)
    RETURN_NAMES = ("value",)
    FUNCTION = "get_value"
    CATEGORY = "EaselHub/Logic"

    def get_value(self, var_name):
        val = EHN_GLOBAL_CACHE.get(var_name.strip(), None)
        if val is None: print(f"[EHN] Var '{var_name}' empty.")
        return (val,)

class EHN_AnySwitch:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "condition": ("BOOLEAN", {"default": True}),
                "on_true": (any_type,),
                "on_false": (any_type,),
            }
        }
    RETURN_TYPES = (any_type,)
    RETURN_NAMES = ("output",)
    FUNCTION = "switch"
    CATEGORY = "EaselHub/Logic"

    def switch(self, condition, on_true, on_false):
        return (on_true if condition else on_false,)

class EHN_BinaryMath:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "a": (any_type,), "b": (any_type,),
                "operation": ([
                    "a + b", "a - b", "a * b", "a / b", "//", "%", "**",
                    "min", "max", "==", "!=", ">", "<", ">=", "<="
                ],),
            }
        }
    RETURN_TYPES = ("INT", "BOOLEAN", "FLOAT")
    FUNCTION = "execute_math"
    CATEGORY = "EaselHub/Logic"

    def execute_math(self, operation, a, b):
        def to_num(x):
            try: return float(x)
            except: return 0.0
        val_a, val_b = to_num(a), to_num(b)
        
        ops = {
            "+": lambda x, y: x + y, "-": lambda x, y: x - y, "*": lambda x, y: x * y,
            "/": lambda x, y: x / y if y!=0 else 0, "//": lambda x, y: x // y, "%": lambda x, y: x % y,
            "**": lambda x, y: x ** y, "min": min, "max": max,
            "==": lambda x, y: 1 if x==y else 0, "!=": lambda x, y: 1 if x!=y else 0,
            ">": lambda x, y: 1 if x>y else 0, "<": lambda x, y: 1 if x<y else 0
        }
        # Simple parsing
        op_key = operation.split(" ")[0] if " " not in operation or len(operation)<3 else operation
        if "a + b" in operation: op_key = "+"
        if "a - b" in operation: op_key = "-"
        if "a * b" in operation: op_key = "*"
        if "a / b" in operation: op_key = "/"

        res = ops.get(op_key, lambda x,y: 0)(val_a, val_b)
        return (int(res), bool(abs(res)>1e-9), float(res))

class EHN_PromptList:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "selection_mode": (["Sequential", "Random (Pick One)", "Shuffle"],),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            },
            "optional": {
                "incoming_list": (any_type,),
                "prompt_1": ("STRING", {"multiline": True, "dynamicPrompts": True}),
                "prompt_2": ("STRING", {"multiline": True, "dynamicPrompts": True}),
                "prompt_3": ("STRING", {"multiline": True, "dynamicPrompts": True}),
                "prompt_4": ("STRING", {"multiline": True, "dynamicPrompts": True}),
                "prompt_5": ("STRING", {"multiline": True, "dynamicPrompts": True}),
            }
        }
    RETURN_TYPES = ("STRING", "STRING", "INT")
    RETURN_NAMES = ("Output List", "Joined String", "Count")
    OUTPUT_IS_LIST = (True, False, False)
    FUNCTION = "process_list"
    CATEGORY = "EaselHub/Logic"

    def process_list(self, selection_mode, seed, incoming_list=None, **kwargs):
        raw_list = []
        if incoming_list:
            if isinstance(incoming_list, list): raw_list.extend([str(x) for x in incoming_list if str(x).strip()])
            elif str(incoming_list).strip(): raw_list.append(str(incoming_list))

        for k in sorted(kwargs.keys()):
            if k.startswith("prompt_") and kwargs[k].strip():
                raw_list.append(kwargs[k].strip())

        if not raw_list: raw_list = [""]
        final_list = raw_list[:]
        
        if "Random" in selection_mode:
            random.seed(seed)
            final_list = [random.choice(raw_list)]
        elif "Shuffle" in selection_mode:
            random.seed(seed)
            random.shuffle(final_list)
            
        return (final_list, "\n".join(final_list), len(final_list))