class EHN_ModelBus:
    CATEGORY = "EaselHub/Utils"
    RETURN_TYPES = ()
    FUNCTION = "run"
    OUTPUT_NODE = True
    
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {}, "optional": {}}

    def run(self, **kwargs):
        return ()
