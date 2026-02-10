import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "EaselHub.ImageCompare",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "EHN_ImageCompare") {
            nodeType.prototype.onExecuted = function(message) {
                if (message && message.images) {
                    this.imgs = message.images.map(img => {
                        const url = `/view?filename=${encodeURIComponent(img.filename)}&type=${img.type}&subfolder=${encodeURIComponent(img.subfolder)}`;
                        const i = new Image();
                        i.src = url;
                        return i;
                    });
                    this.setDirtyCanvas(true, true);
                }
            };
            
            nodeType.prototype.onDrawBackground = function(ctx) {
                if (!this.imgs || this.imgs.length < 2) return;
                if (!this.imgs[0].complete || !this.imgs[1].complete) {
                    this.setDirtyCanvas(true, true);
                    return;
                }
                
                const [w, h] = this.size;
                const imgA = this.imgs[0];
                const imgB = this.imgs[1];
                
                // Keep aspect ratio
                const top_padding = 60;
                const scale = Math.min((w - 20) / imgA.width, (h - top_padding - 10) / imgA.height);
                const dw = imgA.width * scale;
                const dh = imgA.height * scale;
                const dx = (w - dw) / 2;
                const dy = top_padding;

                // Mouse interaction
                const mp = app.canvas.graph_mouse;
                let split = 0.5;
                if (mp[0] >= this.pos[0] + dx && mp[0] <= this.pos[0] + dx + dw &&
                    mp[1] >= this.pos[1] + dy && mp[1] <= this.pos[1] + dy + dh) {
                    split = (mp[0] - (this.pos[0] + dx)) / dw;
                }
                split = Math.max(0, Math.min(1, split));

                ctx.save();
                ctx.beginPath();
                ctx.rect(dx, dy, dw * split, dh);
                ctx.clip();
                ctx.drawImage(imgA, dx, dy, dw, dh);
                ctx.restore();

                ctx.save();
                ctx.beginPath();
                ctx.rect(dx + dw * split, dy, dw * (1 - split), dh);
                ctx.clip();
                ctx.drawImage(imgB, dx, dy, dw, dh);
                ctx.restore();

                ctx.strokeStyle = "rgba(0, 0, 0, 0.5)";
                ctx.lineWidth = 1;
                ctx.beginPath();
                ctx.moveTo(dx + dw * split, dy);
                ctx.lineTo(dx + dw * split, dy + dh);
                ctx.stroke();
                
                ctx.fillStyle = "rgba(255, 255, 255, 0.8)";
                ctx.font = "12px Arial";
                ctx.fillText("A", dx + 5, dy + 15);
                ctx.fillText("B", dx + dw - 15, dy + 15);
            };
        }
    }
});
