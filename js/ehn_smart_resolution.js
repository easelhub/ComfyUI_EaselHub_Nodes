import { app } from "../../scripts/app.js";

// --- Localization Config ---
const I18N = {
    "zh": {
        "model": "模型",
        "res": "分辨率",
        "ratio": "比例",
        "pixels": "像素",
        "tags": {
            "Flux": "Flux.1 / SD3",
            "SDXL": "SDXL / Pony",
            "Video": "视频生成模型",
            "Legacy": "SD 1.5 / 旧版"
        }
    },
    "en": {
        "model": "Model",
        "res": "Size",
        "ratio": "Ratio",
        "pixels": "Pixel",
        "tags": {
            "Flux": "Flux.1 / SD3",
            "SDXL": "SDXL / Pony",
            "Video": "Video Model",
            "Legacy": "Legacy / SD1.5"
        }
    }
};

app.registerExtension({
    name: "Comfy.EaselHubNodes.SmartResolution",
    
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "EHN_SmartResolution") {
            
            // --- 1. Setup Instance & Computation Logic ---
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                const r = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;

                // State storage
                this.ehnData = { w: 0, h: 0, mp: 0, warning: false, tag: "", ratio: "" };
                
                // Force min width for better UX
                if(this.size[0] < 260) this.size[0] = 260;

                // Bind compute method to instance
                this.compute = () => {
                    try {
                        const widgets = this.widgets;
                        if (!widgets || widgets.length < 4) return;

                        const modelStr = widgets[0].value;
                        const modeStr = widgets[1].value;
                        const base = widgets[2].value;
                        const ratioStr = widgets[3].value;
                        
                        // A. Alignment Logic (Must match Python)
                        let align = 8;
                        let rawTag = "Legacy";
                        
                        if (modelStr.includes("Flux") || modelStr.includes("SD 3.5")) {
                            align = 64; rawTag = "Flux";
                        } else if (modelStr.includes("SDXL") || modelStr.includes("Pony")) {
                            align = 32; rawTag = "SDXL";
                        } else if (modelStr.includes("Wan") || modelStr.includes("Video") || modelStr.includes("CogVideo") || modelStr.includes("Hunyuan")) {
                            align = modelStr.includes("Wan") || modelStr.includes("Video") ? 16 : 32;
                            rawTag = "Video";
                        } else if (modelStr.includes("Cascade") || modelStr.includes("SVD") || modelStr.includes("DeepFloyd")) {
                            align = 64; rawTag = "Flux"; // Group high-res together
                        }

                        // B. Ratio Calculation
                        const ratioParts = ratioStr.split(" ")[0].split(":");
                        const ratioVal = parseFloat(ratioParts[0]) / parseFloat(ratioParts[1]);

                        // C. Dimension Calculation
                        let w = 0, h = 0;
                        // Check string content safely
                        if (modeStr && modeStr.includes("Width")) { 
                            w = Math.floor(base / align) * align || align;
                            h = Math.round((w / ratioVal) / align) * align || align;
                        } else { 
                            h = Math.floor(base / align) * align || align;
                            w = Math.round((h * ratioVal) / align) * align || align;
                        }

                        // D. Update State
                        this.ehnData = {
                            w: w, h: h,
                            mp: ((w * h) / 1000000).toFixed(2),
                            warning: (rawTag === "Video" && (w > 1280 || h > 1280)), // Soft warning for video VRAM
                            tagKey: rawTag, // Store key for translation
                            ratio: ratioParts.join(":")
                        };

                    } catch (e) { console.error("[EHN] Calculation Error:", e); }
                    
                    // Request Redraw
                    app.graph.setDirtyCanvas(true, true);
                };

                // Hook into widgets
                for (const w of this.widgets) {
                    if (!w) continue;
                    const originalCallback = w.callback;
                    w.callback = function () {
                        const r = originalCallback ? originalCallback.apply(this, arguments) : undefined;
                        this.compute();
                        return r;
                    }.bind(this);
                }
                
                // Initial Run
                setTimeout(() => this.compute(), 50);
            };

            // --- 2. Handle Reload/Configure ---
            const onConfigure = nodeType.prototype.onConfigure;
            nodeType.prototype.onConfigure = function() {
                if (onConfigure) onConfigure.apply(this, arguments);
                if (this.compute) setTimeout(() => this.compute(), 50);
            };

            // --- 3. Custom UI Painting (The "Smart" Part) ---
            const onDrawForeground = nodeType.prototype.onDrawForeground;
            nodeType.prototype.onDrawForeground = function (ctx) {
                const r = onDrawForeground ? onDrawForeground.apply(this, arguments) : undefined;
                if (this.flags.collapsed) return r;
                if (!this.ehnData) return r;

                // Detect Language
                const langCode = (navigator.language || "en").startsWith("zh") ? "zh" : "en";
                const T = I18N[langCode];

                // Layout Constants
                const margin = 10;
                const lineHeight = 18;
                const headerHeight = 0; // No header inside box
                const contentHeight = (lineHeight * 4) + (margin * 2);
                
                // Dynamic Positioning
                // Find Y position below the last widget
                let bottomWidgetY = 0;
                if (this.widgets && this.widgets.length) {
                    const lastWidget = this.widgets[this.widgets.length - 1];
                    bottomWidgetY = (lastWidget.last_y || 0) + (lastWidget.computedHeight || 28);
                }
                const boxY = Math.max(bottomWidgetY + margin, 50); // Minimum offset
                const totalHeight = boxY + contentHeight + 5;

                // Resize Node if needed (Auto-expand)
                if (this.size[1] < totalHeight) {
                    this.setSize([this.size[0], totalHeight]);
                }

                // Draw Panel
                const boxX = 10;
                const boxW = this.size[0] - 20;

                ctx.save();
                
                // Background
                ctx.beginPath();
                if (ctx.roundRect) ctx.roundRect(boxX, boxY, boxW, contentHeight, 6);
                else ctx.rect(boxX, boxY, boxW, contentHeight);

                // Status Color
                if (this.ehnData.warning) {
                    const grad = ctx.createLinearGradient(boxX, boxY, boxX, boxY + contentHeight);
                    grad.addColorStop(0, "#3a0d0d");
                    grad.addColorStop(1, "#1a0505");
                    ctx.fillStyle = grad;
                    ctx.strokeStyle = "#803030";
                } else {
                    ctx.fillStyle = "#22262e"; // Modern Dark Grey
                    ctx.strokeStyle = "#373c47";
                }
                
                ctx.fill();
                ctx.lineWidth = 1;
                ctx.stroke();

                // Text Content
                const labelColor = "#7d8590";
                const valueColor = this.ehnData.warning ? "#ffbba6" : "#e6edf3";
                
                const modelLabel = T.tags[this.ehnData.tagKey] || this.ehnData.tagKey;
                
                const lines = [
                    { icon: "🧠", label: T.model, value: modelLabel },
                    { icon: "📐", label: T.res,   value: `${this.ehnData.w} x ${this.ehnData.h}` },
                    { icon: "⚖️", label: T.ratio, value: this.ehnData.ratio },
                    { icon: "🔢", label: T.pixels, value: `${this.ehnData.mp} MP` }
                ];

                ctx.font = "12px sans-serif";
                ctx.textBaseline = "middle";
                
                let currentY = boxY + margin + (lineHeight / 2);

                lines.forEach(line => {
                    // Icon
                    ctx.textAlign = "center";
                    ctx.fillStyle = "#fff";
                    ctx.fillText(line.icon, boxX + 20, currentY);

                    // Label
                    ctx.textAlign = "left";
                    ctx.fillStyle = labelColor;
                    ctx.fillText(line.label + ":", boxX + 40, currentY);

                    // Value
                    const labelWidth = ctx.measureText(line.label + ":").width;
                    ctx.fillStyle = valueColor;
                    ctx.font = "600 12px sans-serif"; // Bold value
                    ctx.fillText(line.value, boxX + 40 + labelWidth + 8, currentY);
                    
                    // Reset font for next line
                    ctx.font = "12px sans-serif";
                    currentY += lineHeight;
                });

                ctx.restore();
                return r;
            };
        }
    }
});