import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "EHN.Seed",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "EHN_Seed") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function() {
                if (onNodeCreated) onNodeCreated.apply(this, arguments);
                const w = this.widgets.find(w => w.name === "seed");
                if (w) {
                    this.addWidget("button", "🎲 New Random Seed", null, () => {
                        w.value = Math.floor(Math.random() * 0xffffffffffffffff);
                    });
                }
            };
        }
    }
});
