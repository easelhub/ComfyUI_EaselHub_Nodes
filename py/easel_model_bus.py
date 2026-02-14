class Easel_ModelBus:
    CATEGORY, RETURN_TYPES, FUNCTION, OUTPUT_NODE = "EaselHub/Utils", (), "run", True
    @classmethod
    def INPUT_TYPES(s): return {"required": {}, "optional": {}}
    def run(self, **kwargs): return ()
