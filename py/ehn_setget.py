class EHN_SetNode:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "value": ("*", {}),
        },
        "hidden": {
            "prompt": "PROMPT",
            "extra_pnginfo": "EXTRA_PNGINFO",
            "unique_id": "UNIQUE_ID",
        }}
    RETURN_TYPES = ("*",)
    RETURN_NAMES = ("*",)
    FUNCTION = "set_value"
    CATEGORY = "EaselHub/Utils"

    def set_value(self, value, prompt=None, extra_pnginfo=None, unique_id=None):
        return (value,)

class EHN_GetNode:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "value": ("*", {}),
        }}
    RETURN_TYPES = ("*",)
    RETURN_NAMES = ("*",)
    FUNCTION = "get_value"
    CATEGORY = "EaselHub/Utils"

    def get_value(self, value):
        return (value,)
