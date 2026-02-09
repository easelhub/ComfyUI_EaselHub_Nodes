import math

def to_num(v):
    try: return float(v)
    except: return 0.0

class EHN_MathExpression:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {"expression": ("STRING", {"multiline": False, "default": "a + b"})},
            "optional": {"a": ("*", {"default": 0.0, "forceInput": True}), "b": ("*", {"default": 0.0, "forceInput": True}), "c": ("*", {"default": 0.0, "forceInput": True})}
        }
    RETURN_TYPES = ("INT", "FLOAT")
    RETURN_NAMES = ("int", "float")
    FUNCTION = "execute"
    CATEGORY = "EaselHub Nodes/Number"

    def execute(self, expression, a=0.0, b=0.0, c=0.0):
        try:
            val = eval(expression, {"__builtins__": {}}, {"a": to_num(a), "b": to_num(b), "c": to_num(c), "math": math, "round": round, "abs": abs, "min": min, "max": max, "int": int, "float": float, "pow": pow})
            return (int(val), float(val))
        except: return (0, 0.0)

class EHN_NumberCompare:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "a": ("*", {"default": 0.0, "forceInput": True}),
                "b": ("*", {"default": 0.0, "forceInput": True}),
                "operation": (["a > b", "a < b", "a >= b", "a <= b", "a == b", "a != b"],),
            }
        }
    RETURN_TYPES = ("BOOLEAN", "INT", "FLOAT")
    RETURN_NAMES = ("bool", "int", "float")
    FUNCTION = "execute"
    CATEGORY = "EaselHub Nodes/Number"

    def execute(self, a, b, operation):
        a, b = to_num(a), to_num(b)
        res = {"a > b": a > b, "a < b": a < b, "a >= b": a >= b, "a <= b": a <= b, "a == b": math.isclose(a, b), "a != b": not math.isclose(a, b)}.get(operation, False)
        return (res, 1 if res else 0, 1.0 if res else 0.0)
