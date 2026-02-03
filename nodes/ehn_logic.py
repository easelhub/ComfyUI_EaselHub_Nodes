from .ehn_utils import any_type

class EHN_Math:
    @classmethod
    def INPUT_TYPES(s): return {"required": {"expression": ("STRING", {"default": "a + b"})}, "optional": {"a": (any_type,), "b": (any_type,), "c": (any_type,)}}
    RETURN_TYPES = ("BOOLEAN", "INT", "FLOAT"); FUNCTION = "calc"; CATEGORY = "EaselHub/Logic"
    DESCRIPTION = "Evaluates a math expression using variables a, b, c."
    def calc(self, expression, a=0, b=0, c=0):
        try:
            # Safely cast inputs to float for calculation if possible
            def to_float(v):
                try: return float(v)
                except: return 0.0
            
            d = {"a": to_float(a), "b": to_float(b), "c": to_float(c)}
            # Helper functions for eval
            safe_globals = {"__builtins__": {}, "abs": abs, "min": min, "max": max, "int": int, "float": float, "pow": pow, "round": round}
            # Import math module functions into safe_globals
            import math
            safe_globals.update({k: v for k, v in math.__dict__.items() if not k.startswith("__")})
            
            r = eval(expression, safe_globals, d)
            return (bool(r), int(r), float(r))
        except: return (False, 0, 0.0)

class EHN_ExecutionOrder:
    @classmethod
    def INPUT_TYPES(s): return {"required": {"signal": (any_type,), "value": (any_type,)}}
    RETURN_TYPES = (any_type, any_type); RETURN_NAMES = ("signal", "value"); FUNCTION = "execute"; CATEGORY = "EaselHub/Logic"
    DESCRIPTION = "Forces the 'signal' input to be evaluated before passing 'value' through."
    def execute(self, signal, value): return (signal, value)