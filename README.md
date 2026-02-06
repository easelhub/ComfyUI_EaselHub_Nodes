# ComfyUI EaselHub Nodes

A collection of custom nodes for ComfyUI to enhance your workflow.

## Nodes

### Image
- **🧩EHN Image Tiler**: Split image into tiles with overlap.
- **🧩EHN Image Merger**: Merge tiles back into a single image.
- **📐EHN Image Resize**: Advanced image resizing with various methods (fit, cover, letterbox) and masking support.
- **👁️EHN Image Comparison**: Compare two images side-by-side (saves to temp directory).

### Mask
- **🎭EHN Mask Editor**: Process masks with operations like invert, expand/contract, blur, and fill holes.

### Number / Math
- **🔢EHN Math Expression**: Evaluate mathematical expressions with variables a, b, c.
- **⚖️EHN Number Compare**: Compare two numbers and return boolean/int/float results.

### Utils
- **📏EHN Get Image Size**: Get width, height, and long/short side of an image.
- **🚀EHN System Optimizer**: Utilities to clear VRAM and garbage collection.

## Installation

1. Clone this repository into your `ComfyUI/custom_nodes/` directory:
   ```bash
   cd ComfyUI/custom_nodes/
   git clone https://github.com/yourusername/ComfyUI_EaselHub_Nodes.git
   ```

2. Install dependencies:
   ```bash
   cd ComfyUI_EaselHub_Nodes
   pip install -r requirements.txt
   ```

3. Restart ComfyUI.
