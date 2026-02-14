class EHN_GroupManager:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "version": ("INT", {"default": 1, "min": 1, "max": 100, "hidden": True}),
            },
        }

    RETURN_TYPES = ()
    FUNCTION = "execute"
    CATEGORY = "EaselHub/Utils"

    def execute(self, version):
        return ()
