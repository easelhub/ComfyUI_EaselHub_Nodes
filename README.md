# ComfyUI EaselHub Nodes (EHN)

![ComfyUI](https://img.shields.io/badge/ComfyUI-Extension-4285F4)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Version](https://img.shields.io/badge/Version-2026.1-green)
![License](https://img.shields.io/badge/License-MIT-orange)

**[English](#english-description) | [中文说明](#chinese-description)**

---

<a name="english-description"></a>
## 🇬🇧 English Description

**ComfyUI EaselHub Nodes (EHN)** is a professional suite of custom nodes designed for **Workflow Automation**, **Logic Control**, and **High-Efficiency Image Processing**. 

Built with **2026 Standards**, this suite focuses on robustness, VRAM safety, and "Search-Friendly" usability. It bridges the gap between basic tools and advanced production needs.

### ✨ Key Features (2026 Update)

*   **🧠 Smart Resolution & Latent**: Built-in database for 2026 models (Flux, SD3.5, Hunyuan Video, Wan 2.1, etc.) with VRAM safety checks (8GB optimizations).
*   **🔀 Advanced Logic Control**: Real `If/Else` switching, Global Variable (Wireless) transmission, and mathematical operations.
*   **🧱 Seamless Tiling**: Advanced "Pyramid Blending" algorithm for invisible seams when upscaling using tiling.
*   **🔧 Target MP Resizing**: Resize images by "Total Megapixels" (e.g., "Limit to 2.0MP") to prevent OOM errors dynamically.
*   **📝 Dynamic Prompt Mixer**: Support for Sequential, Random (Gacha), and Shuffled prompt generation with Seed control for reproducibility.

### 💿 Installation

1.  Navigate to your ComfyUI `custom_nodes` directory.
2.  Clone this repository:
    ```bash
    git clone https://github.com/YourUserName/ComfyUI_EaselHub_Nodes.git
    ```
3.  Restart ComfyUI.

### 📦 Node Overview

#### 1. Generation & Latent
*   **`🔍 EHN Aspect Ratio & Latent`**: 
    *   One-stop solution for empty latent generation.
    *   Presets for **Flux, SDXL, Pony, Hunyuan, Wan 2.1**, and Video formats (720p/1080p).
    *   **Smart Warning**: Alerts you if the resolution is too high for your VRAM (especially for 8GB cards).

#### 2. Image Operations
*   **`🔧 EHN Image Resize & Crop`**: 
    *   Modes: Stretch, Crop, Letterbox (Pad), and **Scale to Target MP**.
    *   **Target MP**: Automatically calculates dimensions to match a specific megapixel count (e.g., 2.0 MP) while keeping the aspect ratio.
*   **`🧱 EHN Tile Split (Tiling)`** & **`🏗️ EHN Tile Merge (Blending)`**:
    *   Splits images for tiled processing (upscaling/VAE).
    *   **Feature**: Uses a smoothstep weight mask to perfectly blend tiles, eliminating visible seams or grid artifacts.

#### 3. Logic & Automation
*   **`📡 EHN Set Global Var`** / **`📶 EHN Get Global Var`**: 
    *   Wireless data transmission between distant nodes. Works with any data type.
*   **`🔀 EHN Universal Switch`**: 
    *   A true `If/Else` logic gate. Switches between Model A/B, Image A/B, or Latent A/B based on a Boolean condition.
*   **`📝 EHN Prompt Mixer`**: 
    *   Mixes up to 5 text inputs.
    *   **Modes**: Sequential (Join), Random (Pick One), Shuffle. 
    *   **Seed Control**: Ensures your "Random" choices are reproducible.

#### 4. IO & Utils
*   **`📂 EHN Batch Image Loader`**: 
    *   Loads images from a directory with Metadata (Prompt) support. 
    *   Supports **Random Shuffle** via Seed for testing workflows.
*   **`🧹 EHN VRAM Cleaner`**: Forces Garbage Collection and CUDA Cache clearing.

---

<a name="chinese-description"></a>
## 🇨🇳 中文说明

**ComfyUI EaselHub Nodes (EHN)** 是一套专为 **工作流自动化**、**逻辑控制** 和 **高效图像处理** 设计的专业级节点组。

本插件遵循 **2026 开发标准** 构建，专注于稳定性、显存安全和“搜索友好性”。它填补了基础工具与高级生产环境之间的空白。

### ✨ 核心功能 (2026版更新)

*   **🧠 智能分辨率 (Smart Resolution)**: 内置 2026 主流模型库（Flux, SD3.5, 混元视频, 万相 2.1, Z-Image 等），并针对 8GB 显存提供智能红线预警。
*   **🔀 高级逻辑控制**: 真正的 `If/Else` 开关、全局变量（无线）传输以及数学运算节点。
*   **🧱 无缝分块 (Seamless Tiling)**: 采用“金字塔权重（Pyramid Blending）”算法，完美解决分块放大时的接缝和网格纹理问题。
*   **🔧 像素总量缩放 (Target MP)**: 支持按“总像素量”缩放（例如“限制在 200万像素内”），动态防止显存溢出 (OOM)。
*   **📝 提示词混合器 (Prompt Mixer)**: 支持顺序拼接、随机抽取（抽卡模式）和乱序排列，配合 Seed 种子确保随机结果可复现。

### 💿 安装方法

1.  进入您的 ComfyUI `custom_nodes` 目录。
2.  克隆本仓库：
    ```bash
    git clone https://github.com/YourUserName/ComfyUI_EaselHub_Nodes.git
    ```
3.  重启 ComfyUI。

### 📦 节点概览

#### 1. 生成与潜空间 (Generation)
*   **`🔍 EHN Aspect Ratio & Latent`**: 
    *   集成分辨率计算与 Empty Latent 功能。
    *   预设支持 **Flux, SDXL, Pony, 混元, 可图, 万相** 以及各类视频分辨率 (720p/1080p)。
    *   **智能预警**: 如果分辨率超过显存甜点区（尤其是 8G 显存），UI 会变色警示。

#### 2. 图像操作 (Image Ops)
*   **`🔧 EHN Image Resize & Crop`**: 
    *   模式：拉伸、裁剪、填充 (Letterbox) 以及 **目标像素缩放 (Scale to Target MP)**。
    *   **Target MP**: 自动计算宽高，确保总像素不超过设定值（如 2.0 MP），这是防止 OOM 的神器。
*   **`🧱 EHN Tile Split (Tiling)`** & **`🏗️ EHN Tile Merge (Blending)`**:
    *   用于分块处理（放大或 VAE 解码）。
    *   **特色**: 使用 Smoothstep 平滑权重遮罩进行融合，消除传统分块导致的“十字裂缝”。

#### 3. 逻辑与自动化 (Logic)
*   **`📡 EHN Set Global Var`** / **`📶 EHN Get Global Var`**: 
    *   实现节点间的无线数据传输，支持任意类型，让连线更清爽。
*   **`🔀 EHN Universal Switch`**: 
    *   万能逻辑开关。根据布尔值 (True/False) 在两个输入（模型/图片/Latent）之间自动切换。
*   **`📝 EHN Prompt Mixer`**: 
    *   混合 5 个文本输入框。
    *   **模式**: 顺序连接、随机抽取（抽盲盒）、乱序。
    *   **Seed 控制**: 让您的“随机灵感”可以被固定和复现。

#### 4. 输入输出与工具 (IO & Utils)
*   **`📂 EHN Batch Image Loader`**: 
    *   批量加载文件夹图像，支持提取元数据（Prompt）。
    *   支持通过 Seed 进行 **随机乱序 (Shuffle)** 读取，方便测试工作流鲁棒性。
*   **`🧹 EHN VRAM Cleaner`**: 强制执行 Python 垃圾回收和 CUDA 显存缓存清理。

---

## 📄 License

This project is licensed under the MIT License.