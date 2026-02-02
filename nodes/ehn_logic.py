from .ehn_utils import any_type

class EHN_InputToNumber:
    @classmethod
    def INPUT_TYPES(s): return {"required": {"input_value": (any_type, {"default": 0})}}
    RETURN_TYPES = ("INT", "FLOAT")
    RETURN_NAMES = ("int_value", "float_value")
    FUNCTION = "cast"
    CATEGORY = "EaselHub/Logic"
    def cast(self, input_value):
        try:
            val = float(input_value)
        except:
            val = 0.0
        return (int(val), float(val))

class EHN_BinaryMath:
    @classmethod
    def INPUT_TYPES(s): return {"required": {"a": (any_type,), "b": (any_type,), "operation": (["a + b","a - b","a * b","a / b","a > b","a < b","a >= b","a <= b","a == b","a != b","min (a,b)","max (a,b)","a // b","a % b","a ** b"],)}}
    RETURN_TYPES = ("BOOLEAN", "INT", "FLOAT"); FUNCTION = "do"; CATEGORY = "EaselHub/Logic"
    def do(self, operation, a, b):
        try: a, b = float(a), float(b)
        except: a, b = 0.0, 0.0
        
        op = operation.split("(")[0].strip()
        r = 0
        try:
            if op == "min": r = min(a, b)
            elif op == "max": r = max(a, b)
            elif op == "a + b": r = a + b
            elif op == "a - b": r = a - b
            elif op == "a * b": r = a * b
            elif op == "a / b": r = a / b if b else 0
            elif op == "a // b": r = a // b if b else 0
            elif op == "a % b": r = a % b if b else 0
            elif op == "a ** b": r = a ** b
            elif op == "a > b": r = a > b
            elif op == "a < b": r = a < b
            elif op == "a >= b": r = a >= b
            elif op == "a <= b": r = a <= b
            elif op == "a == b": r = a == b
            elif op == "a != b": r = a != b
        except: r = 0

        # Fix return order to match RETURN_TYPES ("BOOLEAN", "INT", "FLOAT")
        # and handle potential overflow during conversion
        try:
            return (bool(r), int(r), float(r))
        except:
            return (False, 0, 0.0)

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

class EHN_ExecutionOrder:
    @classmethod
    def INPUT_TYPES(s): return {"required": {"signal": (any_type,), "value": (any_type,)}}
    RETURN_TYPES = (any_type, any_type); RETURN_NAMES = ("signal", "value"); FUNCTION = "execute"; CATEGORY = "EaselHub/Logic"
    def execute(self, signal, value): return (signal, value)