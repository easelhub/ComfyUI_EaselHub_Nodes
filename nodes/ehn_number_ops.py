import math
import random

def safe_eval(expr, vars):
    try:
        return eval(expr, {"__builtins__": None}, {
            **vars, "math": math, "random": random, "round": round, "abs": abs, "min": min, "max": max, "int": int, "float": float, "pow": pow
        })
    except: return 0

class EHN_MathExpression:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "expression": ("STRING", {"multiline": True, "default": "a + b"}),
            },
            "optional": {
                "a": ("INT,FLOAT", {"default": 0, "step": 0.01}),
                "b": ("INT,FLOAT", {"default": 0, "step": 0.01}),
                "c": ("INT,FLOAT", {"default": 0, "step": 0.01}),
            }
        }
    RETURN_TYPES = ("INT", "FLOAT")
    FUNCTION = "execute"
    CATEGORY = "EaselHub Nodes/Number"
    def execute(self, expression, a=0, b=0, c=0):
        val = safe_eval(expression, {"a": a, "b": b, "c": c})
        return (int(val), float(val))

class EHN_NumberCompare:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "a": ("INT,FLOAT", {"default": 0, "step": 0.01}),
                "b": ("INT,FLOAT", {"default": 0, "step": 0.01}),
                "op": ([">", "<", ">=", "<=", "==", "!="],),
            }
        }
    RETURN_TYPES = ("BOOLEAN",)
    FUNCTION = "execute"
    CATEGORY = "EaselHub Nodes/Number"
    def execute(self, a, b, op):
        ops = {">": a > b, "<": a < b, ">=": a >= b, "<=": a <= b, "==": math.isclose(a, b), "!=": not math.isclose(a, b)}
        return (ops.get(op, False),)