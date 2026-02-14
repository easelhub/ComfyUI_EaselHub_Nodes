class Easel_GroupManager:
    CATEGORY, RETURN_TYPES, FUNCTION = "EaselHub/Utils", (), "execute"
    @classmethod
    def INPUT_TYPES(s): return {"required": {"version": ("INT", {"default": 1, "min": 1, "max": 100, "hidden": True})}}
    def execute(self, version): return ()
