import torch

# 1. 定义通用类型 (Wildcard Type)
class AnyType(str):
    def __ne__(self, __value: object) -> bool:
        return False

any_type = AnyType("*")

# 2. 全局存储 (Global Storage)
EHN_GLOBAL_CACHE = {}

class EHN_SetVariable:
    """
    Sets a global variable without visible output.
    Forces execution by being an OUTPUT_NODE.
    """
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "input_data": (any_type,),
                "var_name": ("STRING", {"default": "MyVar", "multiline": False}),
            },
            "hidden": {"unique_id": "UNIQUE_ID"},
        }

    RETURN_TYPES = ()
    FUNCTION = "set_value"
    CATEGORY = "EaselHub/Logic"
    OUTPUT_NODE = True

    def set_value(self, input_data, var_name, unique_id=None):
        EHN_GLOBAL_CACHE[var_name] = input_data
        return ()

class EHN_GetVariable:
    """
    Gets a global variable via a dropdown menu.
    """
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                # 默认值只是占位符，JS 会修改它，但后端校验需要被绕过
                "var_name": (["(No Vars Found)"],),
            }
        }
    
    # ----------------------------------------------------------------
    # 🔴 核心修复：增加这个方法来绕过 ComfyUI 的默认校验
    # ----------------------------------------------------------------
    @classmethod
    def VALIDATE_INPUTS(s, var_name):
        # 只要是字符串我们都认为合法，因为列表是前端动态生成的
        # 后端此时还不知道有哪些变量存在（因为 Set 节点还没运行）
        return True

    RETURN_TYPES = (any_type,)
    RETURN_NAMES = ("Value",)
    FUNCTION = "get_value"
    CATEGORY = "EaselHub/Logic"

    def get_value(self, var_name):
        if var_name in EHN_GLOBAL_CACHE:
            val = EHN_GLOBAL_CACHE[var_name]
            return (val,)
        else:
            print(f"[EHN WARNING] Variable '{var_name}' not found. Check execution order or spelling.")
            return (None,)