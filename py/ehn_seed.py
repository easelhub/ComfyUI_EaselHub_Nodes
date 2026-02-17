import random

class EHN_Seed:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {"seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff})}}
    RETURN_TYPES = ("INT",)
    RETURN_NAMES = ("seed",)
    FUNCTION = "execute"
    CATEGORY = "EaselHub/Utils"
    def execute(self, seed):
        return (seed,)
