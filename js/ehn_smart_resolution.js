import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "Comfy.EaselHubNodes.SmartResolution",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "EHN_SmartResolution") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                const r = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;
                this.ehnData = { w: 0, h: 0, mp: 0, warning: 0, tagKey: "", ratio: "", align: 8 };
                if(this.size[0] < 300) this.size[0] = 300;

                this.compute = () => {
                    try {
                        const wModel = this.widgets.find(w => w.name === "model_type");
                        const wMode = this.widgets.find(w => w.name === "calc_mode");
                        const wBase = this.widgets.find(w => w.name === "base_length");
                        const wRatio = this.widgets.find(w => w.name === "aspect_ratio");
                        if (!wModel || !wMode) return;

                        const modelStr = wModel.value;
                        const modeStr = wMode.value;
                        const base = parseInt(wBase.value);
                        const ratioStr = wRatio.value;

                        // Align
                        let align = 32;
                        if (modelStr.includes("Flux") || modelStr.includes("SD 3") || modelStr.includes("Wan") || modelStr.includes("Hunyuan Video")) align = 16;
                        if (modelStr.includes("SD 1.5") || modelStr.includes("SD 2.1") || modelStr.includes("Mochi")) align = 8;
                        if (modelStr.includes("SVD")) align = 64;

                        // Parse
                        let rawTag = modelStr;
                        if (rawTag.includes("] ")) rawTag = rawTag.split("] ")[1].split(" (")[0];

                        let targetRatio = 1.0;
                        let ratioDisplay = "Custom";
                        let isFixedRes = false;
                        let fixedW = 1024, fixedH = 1024;

                        if (ratioStr.includes("x") && !ratioStr.includes(":")) {
                            const dims = ratioStr.split(" ")[0].split("x");
                            fixedW = parseInt(dims[0]); fixedH = parseInt(dims[1]);
                            ratioDisplay = ratioStr.split(" ")[0]; isFixedRes = true;
                        } else if (ratioStr.includes(":")) {
                            const p = ratioStr.split(" ")[0].split(":");
                            targetRatio = parseFloat(p[0]) / parseFloat(p[1]);
                            ratioDisplay = ratioStr.split(" ")[0];
                        }

                        // Calc W/H
                        let w = base, h = base;
                        const getAligned = (val) => Math.max(align, Math.floor(parseInt(val) / align) * align);

                        if (modeStr.includes("Direct")) { w = getAligned(base); h = getAligned(base); ratioDisplay = "Direct"; }
                        else if (isFixedRes) { w = getAligned(fixedW); h = getAligned(fixedH); }
                        else if (modeStr.includes("Fix Width")) { w = getAligned(base); h = getAligned(w / targetRatio); }
                        else if (modeStr.includes("Fix Height")) { h = getAligned(base); w = getAligned(h * targetRatio); }
                        else if (modeStr.includes("Fix Longest")) {
                            if (targetRatio >= 1) { w = getAligned(base); h = getAligned(w / targetRatio); }
                            else { h = getAligned(base); w = getAligned(h * targetRatio); }
                        }
                        else if (modeStr.includes("Fix Shortest")) {
                            if (targetRatio >= 1) { h = getAligned(base); w = getAligned(h * targetRatio); }
                            else { w = getAligned(base); h = getAligned(w / targetRatio); }
                        }

                        const mp = parseFloat(((w * h) / 1000000).toFixed(2));
                        
                        // Warning Logic
                        let warningLevel = 0; 
                        const is8GB = modelStr.includes("[8GB]");
                        const isVideo = modelStr.includes("Video");
                        if (is8GB) {
                            if (mp > 1.4) warningLevel = 1;
                            if (mp > 2.1) warningLevel = 2;
                        } else if (isVideo) {
                            if (mp > 1.2) warningLevel = 1; 
                            if (mp > 2.0) warningLevel = 2;
                        } else if (modelStr.includes("Flux") || modelStr.includes("SDXL")) {
                            if (mp > 2.5) warningLevel = 1;
                            if (mp > 4.5) warningLevel = 2;
                        }

                        this.ehnData = { w, h, mp, warning: warningLevel, tagKey: rawTag, ratio: ratioDisplay, align };

                    } catch (e) {}
                    app.graph.setDirtyCanvas(true, true);
                };

                for (const w of this.widgets) {
                    if(!w) continue;
                    const originalCallback = w.callback;
                    w.callback = function() {
                        if (originalCallback) originalCallback.apply(this, arguments);
                        this.compute();
                    }.bind(this);
                }
                setTimeout(() => this.compute(), 100);
            };

            const onDrawForeground = nodeType.prototype.onDrawForeground;
            nodeType.prototype.onDrawForeground = function (ctx) {
                const r = onDrawForeground ? onDrawForeground.apply(this, arguments) : undefined;
                if (this.flags.collapsed || !this.ehnData) return r;

                const margin = 10, lineHeight = 22;
                const contentHeight = (lineHeight * 4) + (margin * 2);
                let bottomY = 0;
                if (this.widgets && this.widgets.length) {
                    const last = this.widgets[this.widgets.length - 1];
                    bottomY = (last.last_y || 0) + (last.computedHeight || 28);
                }
                const boxY = Math.max(bottomY + margin, 60);
                if (this.size[1] < boxY + contentHeight + 10) this.setSize([this.size[0], boxY + contentHeight + 10]);

                const boxX = 10, boxW = this.size[0] - 20;

                ctx.save();
                ctx.beginPath();
                if (ctx.roundRect) ctx.roundRect(boxX, boxY, boxW, contentHeight, 6);
                else ctx.rect(boxX, boxY, boxW, contentHeight);

                let bgCol1 = "#1e2229", bgCol2 = "#1e2229", strokeCol = "#3e4552", valCol = "#e6edf3";
                if (this.ehnData.warning === 1) { bgCol1 = "#423818"; bgCol2 = "#2e260e"; strokeCol = "#8a732a"; valCol = "#ffdf8c"; }
                else if (this.ehnData.warning === 2) { bgCol1 = "#5e1a1a"; bgCol2 = "#360e0e"; strokeCol = "#c94f4f"; valCol = "#ffbfa6"; }

                const grad = ctx.createLinearGradient(boxX, boxY, boxX, boxY + contentHeight);
                grad.addColorStop(0, bgCol1); grad.addColorStop(1, bgCol2);
                ctx.fillStyle = grad; ctx.strokeStyle = strokeCol; ctx.lineWidth = 1.5;
                ctx.fill(); ctx.stroke();

                const lines = [
                    { icon: "🧠", label: "Model", value: this.ehnData.tagKey },
                    { icon: "📐", label: "Size",   value: `${this.ehnData.w} x ${this.ehnData.h}` },
                    { icon: "⚖️", label: "Ratio", value: this.ehnData.ratio },
                    { icon: "💠", label: "Pixels", value: `${this.ehnData.mp} MP` }
                ];
                if (this.ehnData.warning === 2) lines[3].value += " ⚠️OOM";
                else if (this.ehnData.warning === 1) lines[3].value += " ⚠️Slow";

                ctx.font = "12px sans-serif"; ctx.textBaseline = "middle";
                let curY = boxY + margin + (lineHeight / 2);

                lines.forEach((l, i) => {
                    ctx.textAlign = "center"; ctx.fillStyle = "#fff"; ctx.fillText(l.icon, boxX + 20, curY);
                    ctx.textAlign = "left"; ctx.fillStyle = "#8b949e"; ctx.fillText(l.label, boxX + 40, curY);
                    ctx.textAlign = "right"; ctx.fillStyle = valCol;
                    ctx.font = i === 1 ? "bold 13px sans-serif" : "600 12px sans-serif";
                    let text = l.value;
                    if (i === 1) text += ` (A${this.ehnData.align})`;
                    ctx.fillText(text, boxX + boxW - 15, curY);
                    ctx.font = "12px sans-serif"; curY += lineHeight;
                });
                ctx.restore();
                return r;
            };
        }
    }
});