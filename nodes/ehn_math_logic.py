import torch

class AnyType(str):
    def __ne__(self, __value: object) -> bool:
        return False
any_type = AnyType("*")

class EHN_BinaryMath:
    """
    Performs mathematical or logical operations on two inputs (a, b).
    Inputs 'a' and 'b' are universal types (Int/Float) and must be connected via wires.
    """
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                # 使用 any_type 强制生成输入插槽，而不是面板上的数字输入框
                "a": (any_type,), 
                "b": (any_type,),
                "operation": ([
                    "a + b", 
                    "a - b", 
                    "a * b", 
                    "a / b", 
                    "a // b (Floor Div)", 
                    "a % b (Mod)", 
                    "a ** b (Power)",
                    "a == b", 
                    "a != b", 
                    "a > b", 
                    "a < b", 
                    "a >= b", 
                    "a <= b",
                    "min(a, b)",
                    "max(a, b)"
                ],),
            }
        }

    RETURN_TYPES = ("INT", "BOOLEAN", "FLOAT")
    RETURN_NAMES = ("Int", "Bool", "Float")
    FUNCTION = "execute_math"
    CATEGORY = "EaselHub/Logic"

    def execute_math(self, operation, a, b):
        # 1. 安全类型转换 (Helper to ensure numbers)
        def to_num(x):
            if hasattr(x, "item"): return x.item() # Handle Tensor
            try: return float(x)
            except: return 0.0

        val_a = to_num(a)
        val_b = to_num(b)
        
        res = 0.0
        
        # 2. 执行运算
        if "a + b" in operation: res = val_a + val_b
        elif "a - b" in operation: res = val_a - val_b
        elif "a * b" in operation: res = val_a * val_b
        elif "a / b" in operation: res = val_a / val_b if val_b != 0 else 0
        elif "//" in operation:    res = val_a // val_b if val_b != 0 else 0
        elif "%" in operation:     res = val_a % val_b if val_b != 0 else 0
        elif "**" in operation:    res = val_a ** val_b
        elif "min" in operation:   res = min(val_a, val_b)
        elif "max" in operation:   res = max(val_a, val_b)
        
        # 3. 逻辑运算 (结果为 1 或 0)
        elif "==" in operation: res = 1 if val_a == val_b else 0
        elif "!=" in operation: res = 1 if val_a != val_b else 0
        elif ">=" in operation: res = 1 if val_a >= val_b else 0
        elif "<=" in operation: res = 1 if val_a <= val_b else 0
        elif ">" in operation:  res = 1 if val_a > val_b else 0
        elif "<" in operation:  res = 1 if val_a < val_b else 0
        
        # 4. 构造输出
        # Int: 向下取整或逻辑值的 0/1
        out_int = int(res)
        
        # Bool: 非零即为真 (Python standard)
        out_bool = bool(abs(res) > 1e-9) # 使用 epsilon 处理浮点误差
        
        return (out_int, out_bool, float(res))