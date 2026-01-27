# ComfyUI EaselHub Nodes

[中文](#中文说明) | [English](#english-description)

---

## <a id="中文说明"></a>中文说明

**ComfyUI EaselHub Nodes** 是为 ComfyUI 开发的一组自定义节点集合，旨在提供便捷的工作流工具、LLM 提示词生成集成、图像处理增强以及性能优化功能。

### ✨ 主要功能

1.  **LLM 提示词生成**: 集成了 SiliconFlow, OpenRouter, DeepSeek, OpenAI, Gemini 等多种大模型接口，用于自动生成或优化绘图提示词。支持中英文指令切换。
2.  **TeaCache 性能优化**: 针对 Flux, HunyuanVideo, LTXV, Wan2.1 等模型实现了 TeaCache 加速，通过缓存机制显著提升生成速度。
3.  **逻辑与变量控制**: 提供了全局变量（Set/Get）节点，允许在工作流不同位置传递数据；以及基础的数学运算和逻辑开关。
4.  **图像处理工具**: 包含图像批量加载、尺寸调整、分块/合并、堆叠、对比以及蒙版孔洞填充等实用功能。
5.  **分辨率预设**: 为 Flux, Qwen, Hunyuan 等主流模型提供了推荐的分辨率预设节点，方便快速设置。

### 📦 节点列表

#### 🤖 LLM 集成 (Prompt Gen)
*   **EHN LLM Prompt Gen (SiliconFlow/OpenRouter/DeepSeek/OpenAI/Gemini/Custom)**: 连接各类 LLM API 生成提示词，支持自定义系统提示词和语言设置。

#### 🚀 优化 (Optimization)
*   **EHN TeaCache**: 为 Flux, HunyuanVideo 等模型启用 TeaCache 加速。
*   **EHN Free VRAM**: 强制释放显存。

#### 🛠️ 逻辑与变量 (Logic & Variables)
*   **EHN Set Variable / Get Variable**: 设置和获取全局变量，用于复杂的参数传递。
*   **EHN Any Switch**: 通用的逻辑开关。
*   **EHN Binary Math / Simple Math**: 基础数学运算节点。

#### 🖼️ 图像操作 (Image Operations)
*   **EHN Load Images From Dir**: 从指定目录批量加载图像。
*   **EHN Image Resize**: 图像缩放工具。
*   **EHN Image Split Tiles / Merge Tiles**: 图像分块与合并，常用于放大修复流程。
*   **EHN Image Compare**: 图像对比节点。
*   **EHN Image Stack**: 图像堆叠。
*   **EHN Mask Fill Holes**: 蒙版孔洞填充。
*   **EHN Image Side Calc**: 计算图像边长等信息。

#### 📏 分辨率预设 (Resolutions)
*   提供 Flux, Qwen, ZImage, LTX, Wan, HiDream, Hunyuan 等模型的分辨率选择器。

### 📥 安装方法

1.  进入 ComfyUI 的 `custom_nodes` 目录。
2.  克隆本项目：
    ```bash
    git clone https://github.com/YourUsername/ComfyUI_EaselHub_Nodes.git
    ```
3.  安装依赖（如果有）：
    ```bash
    pip install -r requirements.txt
    ```
4.  重启 ComfyUI。

---

## <a id="english-description"></a>English Description

**ComfyUI EaselHub Nodes** is a collection of custom nodes for ComfyUI, designed to provide convenient workflow utilities, LLM prompt generation integration, image processing enhancements, and performance optimization.

### ✨ Key Features

1.  **LLM Prompt Generation**: Integrates various LLM APIs such as SiliconFlow, OpenRouter, DeepSeek, OpenAI, and Gemini to automatically generate or refine image prompts. Supports switching between English and Chinese instructions.
2.  **TeaCache Optimization**: Implements TeaCache acceleration for models like Flux, HunyuanVideo, LTXV, and Wan2.1, significantly improving generation speed through caching mechanisms.
3.  **Logic & Variable Control**: Provides global variable (Set/Get) nodes for passing data across different parts of the workflow, along with basic math operations and logic switches.
4.  **Image Processing Tools**: Includes utilities for batch image loading, resizing, splitting/merging tiles, stacking, comparing, and mask hole filling.
5.  **Resolution Presets**: Offers recommended resolution presets for popular models like Flux, Qwen, Hunyuan, etc., for quick setup.

### 📦 Node List

#### 🤖 LLM Integration (Prompt Gen)
*   **EHN LLM Prompt Gen (SiliconFlow/OpenRouter/DeepSeek/OpenAI/Gemini/Custom)**: Connects to various LLM APIs to generate prompts, supporting custom system prompts and language settings.

#### 🚀 Optimization
*   **EHN TeaCache**: Enables TeaCache acceleration for supported models (Flux, HunyuanVideo, etc.).
*   **EHN Free VRAM**: Forces VRAM release.

#### 🛠️ Logic & Variables
*   **EHN Set Variable / Get Variable**: Set and get global variables for complex parameter passing.
*   **EHN Any Switch**: A generic logic switch.
*   **EHN Binary Math / Simple Math**: Basic mathematical operation nodes.

#### 🖼️ Image Operations
*   **EHN Load Images From Dir**: Batch load images from a specified directory.
*   **EHN Image Resize**: Image resizing tool.
*   **EHN Image Split Tiles / Merge Tiles**: Image tiling and merging, often used in upscaling workflows.
*   **EHN Image Compare**: Image comparison node.
*   **EHN Image Stack**: Image stacking.
*   **EHN Mask Fill Holes**: Fill holes in masks.
*   **EHN Image Side Calc**: Calculate image dimensions.

#### 📏 Resolution Presets
*   Resolution selectors for Flux, Qwen, ZImage, LTX, Wan, HiDream, Hunyuan, and other models.

### 📥 Installation

1.  Navigate to the `custom_nodes` directory in ComfyUI.
2.  Clone this repository:
    ```bash
    git clone https://github.com/YourUsername/ComfyUI_EaselHub_Nodes.git
    ```
3.  Install dependencies (if any):
    ```bash
    pip install -r requirements.txt
    ```
4.  Restart ComfyUI.
