import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "ComfyUI_EaselHub_Nodes.EHN_ImageStack",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name !== "EHN_ImageStack") return;
        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            onNodeCreated?.apply(this, arguments);
            this.updateInputs = function() {
                const imgIns = this.inputs.filter(i => i.name.startsWith("image_")).sort((a,b)=>parseInt(a.name.split("_")[1])-parseInt(b.name.split("_")[1]));
                if (!imgIns.length) return;
                const last = imgIns[imgIns.length - 1];
                const lastIdx = parseInt(last.name.split("_")[1]);
                if (last.link !== null) {
                    if (!this.inputs.find(i => i.name === `image_${lastIdx + 1}`)) {
                        this.addInput(`image_${lastIdx + 1}`, "IMAGE");
                        this.addInput(`mask_${lastIdx + 1}`, "MASK");
                    }
                } else if (imgIns.length > 1 && imgIns[imgIns.length - 2].link === null) {
                    this.removeInput(this.inputs.findIndex(i => i.name === `mask_${lastIdx}`));
                    this.removeInput(this.inputs.findIndex(i => i.name === last.name));
                }
            };
            const onCon = this.onConnectionsChange;
            this.onConnectionsChange = function (t, i, c, l) {
                onCon?.apply(this, arguments);
                setTimeout(() => this.updateInputs(), 20);
            };
            setTimeout(() => this.updateInputs(), 20);
        };
    }
});