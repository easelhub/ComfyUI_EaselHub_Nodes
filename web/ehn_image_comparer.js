import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

function imageDataToUrl(data) {
    return api.apiURL(`/view?filename=${encodeURIComponent(data.filename)}&type=${data.type}&subfolder=${data.subfolder}${app.getPreviewFormatParam()}${app.getRandParam()}`);
}

class EHN_ImageComparerWidget {
    constructor(name, node) {
        this.name = name;
        this.node = node;
        this.type = "custom";
        this.hitAreas = {};
        this.selected = [];
        this._value = { images: [] };
        this.imgs = [];
    }

    set value(v) {
        let cleanedVal;
        if (Array.isArray(v)) {
            cleanedVal = v.map((d, i) => {
                if (!d || typeof d === "string") d = { url: d, name: i == 0 ? "A" : "B", selected: true };
                return d;
            });
        } else {
            cleanedVal = v.images || [];
        }
        if (cleanedVal.length > 2) {
            const hasAAndB = cleanedVal.some((i) => i.name.startsWith("A")) && cleanedVal.some((i) => i.name.startsWith("B"));
            if (!hasAAndB) cleanedVal = [cleanedVal[0], cleanedVal[1]];
        }
        let selected = cleanedVal.filter((d) => d.selected);
        if (!selected.length && cleanedVal.length) cleanedVal[0].selected = true;
        selected = cleanedVal.filter((d) => d.selected);
        if (selected.length === 1 && cleanedVal.length > 1) cleanedVal.find((d) => !d.selected).selected = true;
        this._value.images = cleanedVal;
        selected = cleanedVal.filter((d) => d.selected);
        this.setSelected(selected);
    }

    get value() { return this._value; }

    setSelected(selected) {
        this._value.images.forEach((d) => (d.selected = false));
        this.imgs.length = 0;
        for (const sel of selected) {
            if (!sel.img) {
                sel.img = new Image();
                sel.img.src = sel.url;
                this.imgs.push(sel.img);
            }
            sel.selected = true;
        }
        this.selected = selected;
    }

    draw(ctx, node, width, y) {
        this.hitAreas = {};
        if (this.value.images.length > 2) {
            ctx.textAlign = "left";
            ctx.textBaseline = "top";
            ctx.font = `14px Arial`;
            const drawData = [];
            const spacing = 5;
            let x = 0;
            for (const img of this.value.images) {
                const w = ctx.measureText(img.name).width;
                drawData.push({ img, text: img.name, x, width: w });
                x += w + spacing;
            }
            x = (node.size[0] - (x - spacing)) / 2;
            for (const d of drawData) {
                ctx.fillStyle = d.img.selected ? "rgba(180, 180, 180, 1)" : "rgba(180, 180, 180, 0.5)";
                ctx.fillText(d.text, x, y);
                this.hitAreas[d.text] = { bounds: [x, y, d.width, 14], data: d.img, onDown: this.onSelectionDown.bind(this) };
                x += d.width + spacing;
            }
            y += 20;
        }
        if (node.properties["comparer_mode"] === "Click") {
            this.drawImage(ctx, this.selected[node.isPointerDown ? 1 : 0], y);
        } else {
            this.drawImage(ctx, this.selected[1], y);
            const cropX = node.isPointerOver ? node.pointerOverPos[0] : (node.lastPointerPos ? node.lastPointerPos[0] : node.size[0] / 2);
            this.drawImage(ctx, this.selected[0], y, cropX);
        }
    }

    onSelectionDown(event, pos, node, bounds) {
        const selected = [...this.selected];
        if (bounds?.data.name.startsWith("A")) selected[0] = bounds.data;
        else if (bounds?.data.name.startsWith("B")) selected[1] = bounds.data;
        this.setSelected(selected);
    }

    drawImage(ctx, image, y, cropX) {
        if (!image?.img?.naturalWidth || !image?.img?.naturalHeight) return;
        let [nodeWidth, nodeHeight] = this.node.size;
        const imageAspect = image.img.naturalWidth / image.img.naturalHeight;
        let height = nodeHeight - y;
        const widgetAspect = nodeWidth / height;
        let targetWidth, targetHeight, offsetX = 0;
        if (imageAspect > widgetAspect) {
            targetWidth = nodeWidth;
            targetHeight = nodeWidth / imageAspect;
        } else {
            targetHeight = height;
            targetWidth = height * imageAspect;
            offsetX = (nodeWidth - targetWidth) / 2;
        }
        const widthMultiplier = image.img.naturalWidth / targetWidth;
        const sourceX = 0, sourceY = 0;
        const sourceWidth = cropX != null ? (cropX - offsetX) * widthMultiplier : image.img.naturalWidth;
        const sourceHeight = image.img.naturalHeight;
        const destX = (nodeWidth - targetWidth) / 2;
        const destY = y + (height - targetHeight) / 2;
        const destWidth = cropX != null ? cropX - offsetX : targetWidth;
        const destHeight = targetHeight;
        ctx.save();
        ctx.beginPath();
        let globalCompositeOperation = ctx.globalCompositeOperation;
        if (cropX) {
            ctx.rect(destX, destY, destWidth, destHeight);
            ctx.clip();
        }
        ctx.drawImage(image.img, sourceX, sourceY, sourceWidth, sourceHeight, destX, destY, destWidth, destHeight);
        if (cropX != null && cropX >= (nodeWidth - targetWidth) / 2 && cropX <= targetWidth + offsetX) {
            ctx.beginPath();
            ctx.moveTo(cropX, destY);
            ctx.lineTo(cropX, destY + destHeight);
            ctx.globalCompositeOperation = "difference";
            ctx.strokeStyle = "rgba(255,255,255, 1)";
            ctx.stroke();
        }
        ctx.globalCompositeOperation = "source-over";
        ctx.font = "bold 16px Arial";
        ctx.fillStyle = "rgba(255, 255, 255, 0.8)";
        ctx.shadowColor = "rgba(0, 0, 0, 0.8)";
        ctx.shadowBlur = 4;
        ctx.textAlign = "left";
        ctx.fillText("A", 5, nodeHeight - 5);
        ctx.textAlign = "right";
        ctx.fillText("B", nodeWidth - 5, nodeHeight - 5);
        ctx.globalCompositeOperation = globalCompositeOperation;
        ctx.restore();
    }

    computeSize(width) { return [width, 20]; }

    serializeValue(node, index) {
        const v = [];
        for (const data of this._value.images) {
            const d = { ...data };
            delete d.img;
            v.push(d);
        }
        return { images: v };
    }
    
    mouse(event, pos, node) {
        if (event.type == "pointerdown") {
            for (const part of Object.values(this.hitAreas)) {
                if (pos[0] >= part.bounds[0] && pos[0] <= part.bounds[0] + part.bounds[2] && pos[1] >= part.bounds[1] && pos[1] <= part.bounds[1] + part.bounds[3]) {
                    if (part.onDown) {
                        part.onDown(event, pos, node, part);
                        return true;
                    }
                }
            }
        }
        return false;
    }
}

app.registerExtension({
    name: "EHN.ImageComparer",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "EHN_ImageComparer") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                onNodeCreated?.apply(this, arguments);
                this.canvasWidget = this.addCustomWidget(new EHN_ImageComparerWidget("ehn_comparer", this));
                this.setSize([400, 300]);
                this.properties["comparer_mode"] = "Slide";
                this.isPointerDown = false;
                this.isPointerOver = false;
                this.pointerOverPos = [0, 0];
                this.lastPointerPos = null;
            };

            nodeType.prototype.onExecuted = function (output) {
                if ("images" in output) {
                    this.canvasWidget.value = {
                        images: (output.images || []).map((d, i) => {
                            return { name: i === 0 ? "A" : "B", selected: true, url: imageDataToUrl(d) };
                        }),
                    };
                } else {
                    output.a_images = output.a_images || [];
                    output.b_images = output.b_images || [];
                    const imagesToChoose = [];
                    const multiple = output.a_images.length + output.b_images.length > 2;
                    for (const [i, d] of output.a_images.entries()) imagesToChoose.push({ name: output.a_images.length > 1 || multiple ? `A${i + 1}` : "A", selected: i === 0, url: imageDataToUrl(d) });
                    for (const [i, d] of output.b_images.entries()) imagesToChoose.push({ name: output.b_images.length > 1 || multiple ? `B${i + 1}` : "B", selected: i === 0, url: imageDataToUrl(d) });
                    this.canvasWidget.value = { images: imagesToChoose };
                }
            };

            nodeType.prototype.onSerialize = function (serialised) {
                if (this.canvasWidget) {
                    serialised.widgets_values = serialised.widgets_values || [];
                    serialised.widgets_values[this.widgets.indexOf(this.canvasWidget)] = this.canvasWidget.serializeValue().images;
                }
            };

            nodeType.prototype.onMouseDown = function (event, pos, canvas) { this.isPointerDown = true; return false; };
            nodeType.prototype.onMouseEnter = function (event) { this.isPointerDown = !!app.canvas.pointer_is_down; this.isPointerOver = true; };
            nodeType.prototype.onMouseLeave = function (event) { this.isPointerDown = false; this.isPointerOver = false; };
            nodeType.prototype.onMouseMove = function (event, pos, canvas) { this.pointerOverPos = [...pos]; this.lastPointerPos = [...pos]; };
            
            Object.defineProperty(nodeType.prototype, "comparer_mode", {
                get() { return this.properties["comparer_mode"]; },
                set(v) { this.properties["comparer_mode"] = v; }
            });
        }
    },
});
