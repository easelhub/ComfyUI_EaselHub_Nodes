import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "EHN.ModelBus",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "EHN_ModelBus") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function() {
                if (onNodeCreated) onNodeCreated.apply(this, arguments);
                if (!this.inputs || this.inputs.length === 0) this.addInput("*", "*");
            };

            const onConnectionsChange = nodeType.prototype.onConnectionsChange;
            nodeType.prototype.onConnectionsChange = function(type, index, connected, link_info, slot) {
                if (onConnectionsChange) onConnectionsChange.apply(this, arguments);
                if (type !== 1) return;
                setTimeout(() => {
                    if (connected && link_info) {
                        const link = app.graph.links[link_info.link];
                        if (link && this.inputs[index]) {
                            this.inputs[index].name = link.type;
                            this.inputs[index].type = link.type;
                        }
                    } else if (!connected && this.inputs[index]) {
                        if (index !== this.inputs.length - 1) { 
                            this.removeInput(index);
                        } else {
                            this.inputs[index].name = "*";
                            this.inputs[index].type = "*";
                        }
                    }
                    
                    const last = this.inputs[this.inputs.length - 1];
                    if (last && last.link !== null) this.addInput("*", "*");
                    
                    this.setSize(this.computeSize());
                }, 20);
            };
        }
    },

    async setup() {
        const api = app.api;
        const originalQueuePrompt = api.queuePrompt;
        api.queuePrompt = async function(number, {output}) {
            const busSources = {};
            for (const nodeId in output) {
                const node = output[nodeId];
                if (node.class_type === "EHN_ModelBus" && node.inputs) {
                    for (const [name, value] of Object.entries(node.inputs)) {
                        if (Array.isArray(value) && name !== "*") busSources[name] = value;
                    }
                }
            }
            if (Object.keys(busSources).length > 0) {
                const nodeDefs = await api.getNodeDefs();
                for (const nodeId in output) {
                    const node = output[nodeId];
                    if (node.class_type === "EHN_ModelBus") continue;
                    const def = nodeDefs[node.class_type];
                    if (!def || !def.input) continue;
                    const inject = (inputs, config) => {
                        if (!inputs) return;
                        for (const [inputName, inputConfig] of Object.entries(config)) {
                            const type = inputConfig[0];
                            if (busSources[type] && !node.inputs[inputName]) node.inputs[inputName] = busSources[type];
                        }
                    };
                    if (def.input.required) inject(node.inputs, def.input.required);
                    if (def.input.optional) inject(node.inputs, def.input.optional);
                }
            }
            return originalQueuePrompt.apply(this, arguments);
        };
    }
});
