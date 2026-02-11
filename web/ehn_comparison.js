import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

app.registerExtension({
    name: "EaselHub.ImageComparison",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "EHN_ImageComparison") {
            nodeType.prototype.onExecuted = function(message) {
                if (message && message.images && message.images.length >= 2) {
                    this.imgs = [new Image(), new Image()];
                    const t = Date.now();
                    this.imgs[0].src = api.apiURL(`/view?filename=${message.images[0].filename}&type=${message.images[0].type}&subfolder=${message.images[0].subfolder}&t=${t}`);
                    this.imgs[1].src = api.apiURL(`/view?filename=${message.images[1].filename}&type=${message.images[1].type}&subfolder=${message.images[1].subfolder}&t=${t}`);
                    
                    const updateSize = () => {
                        if (this.imgs[0].complete && this.imgs[1].complete) {
                            const w1 = this.imgs[0].width, h1 = this.imgs[0].height;
                            const w2 = this.imgs[1].width, h2 = this.imgs[1].height;
                            const ratio = Math.max(w1/h1, w2/h2);
                            this.setSize([this.size[0], this.size[0] / ratio + 60]);
                            app.graph.setDirtyCanvas(true, true);
                        }
                    };
                    this.imgs[0].onload = updateSize;
                    this.imgs[1].onload = updateSize;
                }
            };

            nodeType.prototype.onDrawBackground = function(ctx) {
                if (this.imgs && this.imgs[0].complete && this.imgs[1].complete) return;
            };
            
            nodeType.prototype.onDrawForeground = function(ctx) {
                if (!this.imgs || !this.imgs[0].complete || !this.imgs[1].complete) return;

                const w = this.size[0];
                const h = this.size[1] - 60; 
                const y = 60;
                
                let splitX = w / 2;
                if (app.canvas.graph_mouse) {
                    const mx = app.canvas.graph_mouse[0] - this.pos[0];
                    const my = app.canvas.graph_mouse[1] - this.pos[1];
                    if (mx >= 0 && mx <= w && my >= y && my <= y + h) splitX = mx;
                }

                const drawImg = (img, clipRect) => {
                    const imgW = img.width;
                    const imgH = img.height;
                    const scale = Math.min(w / imgW, h / imgH);
                    const drawW = imgW * scale;
                    const drawH = imgH * scale;
                    const offX = (w - drawW) / 2;
                    const offY = y + (h - drawH) / 2;

                    ctx.save();
                    ctx.beginPath();
                    ctx.rect(clipRect[0], clipRect[1], clipRect[2], clipRect[3]);
                    ctx.clip();
                    ctx.drawImage(img, offX, offY, drawW, drawH);
                    ctx.restore();
                };

                drawImg(this.imgs[0], [0, y, splitX, h]);
                drawImg(this.imgs[1], [splitX, y, w - splitX, h]);

                ctx.strokeStyle = "rgba(0, 0, 0, 0.5)";
                ctx.lineWidth = 1;
                ctx.beginPath();
                ctx.moveTo(splitX, y);
                ctx.lineTo(splitX, y + h);
                ctx.stroke();

                ctx.fillStyle = "rgba(0,0,0,0.5)";
                ctx.fillRect(5, y + 5, 20, 20);
                ctx.fillRect(w - 25, y + 5, 20, 20);
                ctx.fillStyle = "#fff";
                ctx.font = "14px Arial";
                ctx.fillText("A", 10, y + 20);
                ctx.fillText("B", w - 20, y + 20);
            };
        }
    }
});