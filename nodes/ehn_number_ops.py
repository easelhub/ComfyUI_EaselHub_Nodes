import math

def to_num(v):
    if isinstance(v, (int, float)):
        return v
    try:
        return float(v)
    except:
        return 0.0

class EHN_MathExpression:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "expression": ("STRING", {"multiline": False, "default": "a + b"}),
            },
            "optional": {
                "a": ("*", {"default": 0.0, "forceInput": True}),
                "b": ("*", {"default": 0.0, "forceInput": True}),
                "c": ("*", {"default": 0.0, "forceInput": True}),
            }
        }
    RETURN_TYPES = ("INT", "FLOAT")
    RETURN_NAMES = ("int", "float")
    FUNCTION = "execute"
    CATEGORY = "EaselHub Nodes/Number"

    def execute(self, expression, a=0.0, b=0.0, c=0.0):
        a = to_num(a)
        b = to_num(b)
        c = to_num(c)
        g_vars = {"a": a, "b": b, "c": c, "math": math, "round": round, "abs": abs, "min": min, "max": max, "int": int, "float": float, "pow": pow}
        try:
            val = eval(expression, {"__builtins__": {}}, g_vars)
            return (int(val), float(val))
        except Exception as e:
            print(f"EHN Math Expression Error: {e}")
            return (0, 0.0)

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
        a = to_num(a)
        b = to_num(b)
        res = False
        if operation == "a > b": res = a > b
        elif operation == "a < b": res = a < b
        elif operation == "a >= b": res = a >= b
        elif operation == "a <= b": res = a <= b
        elif operation == "a == b": res = math.isclose(a, b)
        elif operation == "a != b": res = not math.isclose(a, b)
        return (res, 1 if res else 0, 1.0 if res else 0.0)
