import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "EHN.ModelBus",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "EHN_ModelBus") {
            
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function() {
                if (onNodeCreated) onNodeCreated.apply(this, arguments);
                if (!this.inputs || this.inputs.length === 0) {
                    this.addInput("*", "*");
                }
            };

            const onConnectionsChange = nodeType.prototype.onConnectionsChange;
            nodeType.prototype.onConnectionsChange = function(type, index, connected, link_info, slot) {
                if (onConnectionsChange) onConnectionsChange.apply(this, arguments);
                if (type !== 1) return; // Only input changes

                // We'll use a deferred update to handle multiple rapid changes and ensure state is stable
                setTimeout(() => {
                    this.updateInputs();
                }, 20);
            };

            nodeType.prototype.updateInputs = function() {
                // 1. Remove unconnected slots (except the last one if it's *)
                // Iterate backwards to safely remove
                for (let i = this.inputs.length - 1; i >= 0; i--) {
                    const slot = this.inputs[i];
                    // If it's unconnected
                    if (slot.link === null) {
                        // If it's NOT the last slot, remove it
                        if (i !== this.inputs.length - 1) {
                            this.removeInput(i);
                        }
                    }
                }

                // 2. Update names/types of connected slots
                for (let i = 0; i < this.inputs.length; i++) {
                    const slot = this.inputs[i];
                    if (slot.link !== null) {
                        const link = app.graph.links[slot.link];
                        if (link) {
                            if (slot.name !== link.type || slot.type !== link.type) {
                                slot.name = link.type;
                                slot.type = link.type;
                            }
                        }
                    } else {
                        // Unconnected slot (should be the last one)
                        if (slot.name !== "*" || slot.type !== "*") {
                            slot.name = "*";
                            slot.type = "*";
                        }
                    }
                }

                // 3. Ensure the last slot is empty and wildcard
                const lastSlot = this.inputs[this.inputs.length - 1];
                if (lastSlot && lastSlot.link !== null) {
                    this.addInput("*", "*");
                } else if (!lastSlot) {
                     this.addInput("*", "*");
                }
                
                this.setSize(this.computeSize());
            };
        }
    },

    async setup() {
        const api = app.api;
        const originalQueuePrompt = api.queuePrompt;

        api.queuePrompt = async function(number, {output}) {
            const busSources = {}; // Map of Type -> Source [NodeID, SlotIndex]

            // 1. Collect sources from all EHN_ModelBus nodes
            for (const nodeId in output) {
                const node = output[nodeId];
                if (node.class_type === "EHN_ModelBus") {
                    if (node.inputs) {
                        for (const [name, value] of Object.entries(node.inputs)) {
                            if (Array.isArray(value)) {
                                if (name !== "*") {
                                    busSources[name] = value;
                                }
                            }
                        }
                    }
                }
            }

            // 2. Inject into unconnected inputs
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
                            if (busSources[type] && !node.inputs[inputName]) {
                                node.inputs[inputName] = busSources[type];
                            }
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
