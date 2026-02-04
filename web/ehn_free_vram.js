import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "EaselHub.FreeVRAM",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "EHN_FreeVRAM") {
            const onConnectionsChange = nodeType.prototype.onConnectionsChange;
            nodeType.prototype.onConnectionsChange = function (type, index, connected, link_info) {
                if (onConnectionsChange) onConnectionsChange.apply(this, arguments);
                
                // Type 1 is Input. We want to react when 'any_input' changes.
                if (type === 1) {
                    const input = this.inputs[index];
                    if (input.name === "any_input") {
                        if (connected) {
                            const link = app.graph.links[link_info.id];
                            if (link) {
                                const originNode = app.graph.getNodeById(link.origin_id);
                                if (originNode) {
                                    const originType = originNode.outputs[link.origin_slot].type;
                                    // Update output type to match input type
                                    if (this.outputs && this.outputs[0]) {
                                        this.outputs[0].type = originType;
                                        this.outputs[0].name = originType;
                                    }
                                }
                            }
                        } else {
                            // Disconnected, revert to wildcard
                            if (this.outputs && this.outputs[0]) {
                                this.outputs[0].type = "*";
                                this.outputs[0].name = "any_type";
                            }
                        }
                    }
                }
            };
        }
    }
});
