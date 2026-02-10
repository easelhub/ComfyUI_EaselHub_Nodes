
---

### 📝 文件 2: `02_Python后端开发_核心篇.md`

```markdown
# 02. Python 后端开发 (核心篇)

## 1. 节点类模板 (Copy-Paste Ready)

```python
class MyNodeTemplate:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        """
        定义输入参数。
        返回字典结构：{"required": {}, "optional": {}, "hidden": {}}
        """
        return {
            "required": {
                # 格式: "参数名": ("类型", {配置})
                "image": ("IMAGE",), 
                "int_value": ("INT", {
                    "default": 20, 
                    "min": 1, 
                    "max": 100, 
                    "step": 1, 
                    "display": "number" # "number" | "slider"
                }),
                "float_value": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 10.0, "step": 0.01}),
                "string_value": ("STRING", {"multiline": True, "dynamicPrompts": True}),
                "dropdown": (["option1", "option2", "option3"],), # 下拉菜单
                "bool_value": ("BOOLEAN", {"default": True}),
            },
            "optional": {
                # 可选输入，如果在 UI 上未连接，函数接收到的值为 None
                "optional_model": ("MODEL",),
            },
            "hidden": {
                # 系统自动注入的参数，不在 UI 显示
                "unique_id": "UNIQUE_ID",
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO",
            }
        }

    RETURN_TYPES = ("IMAGE", "INT", "STRING")
    RETURN_NAMES = ("Output Image", "Count", "Log") # 自定义输出端口名称
    FUNCTION = "execute_logic" # 执行入口函数名
    CATEGORY = "MyPack/Utils"  # 右键菜单路径

    def execute_logic(self, image, int_value, float_value, string_value, dropdown, bool_value, optional_model=None):
        # Python 处理逻辑
        print(f"Processing: {string_value}")
        
        # 即使只有一个返回值，也必须是元组！
        return (image, int_value, "Done")