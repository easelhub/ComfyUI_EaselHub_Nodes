import math
import random

class EHN_MathExpression:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "expression": ("STRING", {"multiline": False, "default": "a + b"}),
            },
            "optional": {
                "a": ("FLOAT", {"default": 0.0, "step": 0.01, "forceInput": True}),
                "b": ("FLOAT", {"default": 0.0, "step": 0.01, "forceInput": True}),
                "c": ("FLOAT", {"default": 0.0, "step": 0.01, "forceInput": True}),
            }
        }
    RETURN_TYPES = ("INT", "FLOAT")
    RETURN_NAMES = ("int", "float")
    FUNCTION = "execute"
    CATEGORY = "EaselHub/Logic"

    def execute(self, expression, a=0.0, b=0.0, c=0.0):
        try:
            env = {"a": a, "b": b, "c": c, "math": math, "random": random, "int": int, "float": float, "round": round, "abs": abs, "max": max, "min": min, "pow": pow}
            res = eval(expression, {"__builtins__": {}}, env)
            return (int(res), float(res))
        except: return (0, 0.0)

class EHN_NumberCompare:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "a": ("FLOAT", {"default": 0.0, "step": 0.01, "forceInput": True}),
                "b": ("FLOAT", {"default": 0.0, "step": 0.01, "forceInput": True}),
                "operator": (["==", "!=", ">", "<", ">=", "<="], {"default": "=="}),
            }
        }
    RETURN_TYPES = ("BOOLEAN",)
    RETURN_NAMES = ("bool",)
    FUNCTION = "execute"
    CATEGORY = "EaselHub/Logic"

    def execute(self, a, b, operator):
        ops = {
            "==": lambda x, y: x == y,
            "!=": lambda x, y: x != y,
            ">": lambda x, y: x > y,
            "<": lambda x, y: x < y,
            ">=": lambda x, y: x >= y,
            "<=": lambda x, y: x <= y
        }
        return (ops[operator](a, b),)
