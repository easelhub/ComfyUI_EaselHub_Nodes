
---

### 📝 文件 3: `03_数据流与Tensor操作_进阶篇.md`

```markdown
# 03. 数据流与 Tensor 操作 (进阶篇)

ComfyUI 的核心是 PyTorch Tensor。理解数据形状 (Shape) 是开发的重中之重。

## 1. 图像 (IMAGE)
ComfyUI 的图像与 OpenCV/PIL 的表示方式完全不同。

*   **类型**: `torch.Tensor` (float32)
*   **形状**: `[Batch_Size, Height, Width, Channels]` (BHWC)
*   **范围**: `0.0` (黑) 到 `1.0` (白)
*   **通道**: RGB (3通道)。

### 常用转换代码库

#### 1.1 Tensor 转 PIL (用于保存或使用 PIL 库处理)
```python
import torch
from PIL import Image
import numpy as np

def tensor2pil(image_tensor):
    # 输入: [B, H, W, C]
    # 取第一张图
    batch_image = image_tensor[0] 
    # 转换为 numpy: [H, W, C], 0-1
    i = 255. * batch_image.cpu().numpy() 
    # 转换为 PIL
    img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
    return img