from .ehn_utils import any_type

class EHN_AnySwitch:
    @classmethod
    def INPUT_TYPES(s): return {"required": {"condition": ("BOOLEAN", {"default": True}), "on_true": (any_type,), "on_false": (any_type,)}}
    RETURN_TYPES = (any_type,); FUNCTION = "switch"; CATEGORY = "EaselHub/Logic"
    def switch(self, condition, on_true, on_false): return (on_true if condition else on_false,)

class EHN_BinaryMath:
    @classmethod
    def INPUT_TYPES(s): return {"required": {"a": (any_type,), "b": (any_type,), "operation": (["a + b","a - b","a * b","a / b","a > b","a < b","a >= b","a <= b","a == b","a != b","min (a,b)","max (a,b)","a // b","a % b","a ** b"],)}}
    RETURN_TYPES = ("BOOLEAN", "INT", "FLOAT"); FUNCTION = "do"; CATEGORY = "EaselHub/Logic"
    def do(self, operation, a, b):
        try: a, b = float(a), float(b)
        except: a, b = 0.0, 0.0
        op = operation.split("(")[0].strip()
        r = {"min":min(a,b),"max":max(a,b),"a + b":a+b,"a - b":a-b,"a * b":a*b,"a / b":a/b if b else 0,"a // b":a//b if b else 0,"a % b":a%b if b else 0,"a ** b":a**b,"a > b":a>b,"a < b":a<b,"a >= b":a>=b,"a <= b":a<=b,"a == b":a==b,"a != b":a!=b}.get(op, 0)
        return (int(r), bool(r), float(r))

class EHN_SimpleMath:
    @classmethod
    def INPUT_TYPES(s): return {"required": {"expression": ("STRING", {"default": "a + b"})}, "optional": {"a": (any_type,), "b": (any_type,), "c": (any_type,)}}
    RETURN_TYPES = ("INT", "FLOAT", "BOOLEAN"); FUNCTION = "calc"; CATEGORY = "EaselHub/Logic"
    def calc(self, expression, a=0, b=0, c=0):
        try:
            d = {k:float(v) for k,v in zip("abc",[a,b,c]) if str(v).replace('.','',1).isdigit()}
            r = eval(expression, {"__builtins__":{}}, {**d, "abs":abs,"min":min,"max":max,"int":int,"float":float,"pow":pow,"math":__import__("math")})
            return (int(r), float(r), bool(r))
        except: return (0, 0.0, False)