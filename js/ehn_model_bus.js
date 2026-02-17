import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "EHN.ModelBus",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "EHN_ModelBus") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function() {
                onNodeCreated?.apply(this, arguments);
                if (!this.inputs?.length) this.addInput("*", "*");
            };

            const onConnectionsChange = nodeType.prototype.onConnectionsChange;
            nodeType.prototype.onConnectionsChange = function(type, index, connected, link_info, slot) {
                onConnectionsChange?.apply(this, arguments);
                if (type !== 1) return;
                setTimeout(() => this.updateInputs(), 20);
            };

            nodeType.prototype.updateInputs = function() {
                for (let i = this.inputs.length - 2; i >= 0; i--) {
                    if (!this.inputs[i].link) this.removeInput(i);
                }
                for (let i = 0; i < this.inputs.length; i++) {
                    const link = this.inputs[i].link ? app.graph.links[this.inputs[i].link] : null;
                    const type = link ? link.type : "*";
                    if (this.inputs[i].type !== type) {
                        this.inputs[i].type = type;
                        this.inputs[i].name = type;
                    }
                }
                if (this.inputs[this.inputs.length - 1].link) this.addInput("*", "*");
                this.setSize(this.computeSize());
            };
        }
    },

    async setup() {
        const api = app.api;
        const originalQueuePrompt = api.queuePrompt;
        api.queuePrompt = async function(number, {output}) {
            const busSources = {};
            for (const id in output) {
                if (output[id].class_type === "EHN_ModelBus" && output[id].inputs) {
                    for (const [k, v] of Object.entries(output[id].inputs)) {
                        if (Array.isArray(v) && k !== "*") busSources[k] = v;
                    }
                }
            }
            if (Object.keys(busSources).length) {
                const nodeDefs = await api.getNodeDefs();
                for (const id in output) {
                    if (output[id].class_type === "EHN_ModelBus") continue;
                    const def = nodeDefs[output[id].class_type];
                    if (!def?.input) continue;
                    const inject = (inputs, config) => {
                        if (!inputs) return;
                        for (const [k, v] of Object.entries(config)) {
                            if (busSources[v[0]] && !output[id].inputs[k]) output[id].inputs[k] = busSources[v[0]];
                        }
                    };
                    inject(output[id].inputs, def.input.required);
                    inject(output[id].inputs, def.input.optional);
                }
            }
            return originalQueuePrompt.apply(this, arguments);
        };
    }
});