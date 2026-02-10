import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "EaselHub.ImageComparison",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "EHN_ImageComparison") {
            nodeType.prototype.onExecuted = function(message) {
                if (message && message.ehn_comparison_images && message.ehn_comparison_images.length >= 2) {
                    if (!this.ehn_imgs) this.ehn_imgs = [new Image(), new Image()];
                    for (let i = 0; i < 2; i++) {
                        this.ehn_imgs[i].src = `./view?filename=${message.ehn_comparison_images[i].filename}&type=${message.ehn_comparison_images[i].type}&subfolder=${message.ehn_comparison_images[i].subfolder}&t=${Date.now()}`;
                    }
                    this.ehn_imgs[0].onload = () => {
                         this.setSize([this.size[0], Math.max(100, (this.size[0] / (this.ehn_imgs[0].width / this.ehn_imgs[0].height)) + 50)]);
                         this.setDirtyCanvas(true, true);
                    }
                }
            };
            nodeType.prototype.onDrawForeground = function(ctx) {
                if (!this.ehn_imgs || !this.ehn_imgs[0].complete || !this.ehn_imgs[1].complete || this.flags.collapsed) return;
                const w = this.size[0], h = this.size[1], headerHeight = 50, availH = h - headerHeight;
                if (availH <= 0) return;
                const scale = Math.min(w / this.ehn_imgs[0].width, availH / this.ehn_imgs[0].height);
                const drawW = this.ehn_imgs[0].width * scale, drawH = this.ehn_imgs[0].height * scale;
                const offX = (w - drawW) / 2, offY = headerHeight + (availH - drawH) / 2;
                let split = w / 2;
                if (app.canvas.graph_mouse) {
                    const local = [app.canvas.graph_mouse[0] - this.pos[0], app.canvas.graph_mouse[1] - this.pos[1]];
                    if (local[0] >= 0 && local[0] <= w && local[1] >= 0 && local[1] <= h) split = local[0];
                }
                ctx.save(); ctx.beginPath(); ctx.rect(0, headerHeight, split, h - headerHeight); ctx.clip();
                ctx.drawImage(this.ehn_imgs[0], offX, offY, drawW, drawH); ctx.restore();
                ctx.save(); ctx.beginPath(); ctx.rect(split, headerHeight, w - split, h - headerHeight); ctx.clip();
                ctx.drawImage(this.ehn_imgs[1], offX, offY, drawW, drawH); ctx.restore();
                ctx.strokeStyle = "rgba(0, 0, 0, 0.5)"; ctx.lineWidth = 1; ctx.beginPath(); ctx.moveTo(split, headerHeight); ctx.lineTo(split, h); ctx.stroke();
                ctx.font = "bold 14px Arial";
                if (split > offX + 20) { ctx.fillStyle = "rgba(0,0,0,0.5)"; ctx.fillRect(offX + 5, offY + drawH - 25, 24, 20); ctx.fillStyle = "#FFF"; ctx.fillText("A", offX + 12, offY + drawH - 10); }
                if (split < offX + drawW - 20) { ctx.fillStyle = "rgba(0,0,0,0.5)"; ctx.fillRect(offX + drawW - 29, offY + drawH - 25, 24, 20); ctx.fillStyle = "#FFF"; ctx.fillText("B", offX + drawW - 22, offY + drawH - 10); }
            };
        }
    }
});