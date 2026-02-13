import { app } from "../../scripts/app.js";
import { ComfyWidgets } from "../../scripts/widgets.js";

const LAST_SEED_BUTTON_LABEL = "♻️ (Use Last Queued Seed)";

const SPECIAL_SEED_RANDOM = -1;
const SPECIAL_SEED_INCREMENT = -2;
const SPECIAL_SEED_DECREMENT = -3;
const SPECIAL_SEEDS = [SPECIAL_SEED_RANDOM, SPECIAL_SEED_INCREMENT, SPECIAL_SEED_DECREMENT];

app.registerExtension({
    name: "EHN.Seed",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "EHN_Seed") {
            
            nodeType.prototype.onNodeCreated = function () {
                this.serialize_widgets = true;
                this.properties = this.properties || {};
                this.properties["randomMax"] = 1125899906842624;
                this.properties["randomMin"] = 0;
                this.lastSeed = undefined;

                // Grab the already available widgets, and remove the built-in control_after_generate
                for (let i = this.widgets.length - 1; i >= 0; i--) {
                    const w = this.widgets[i];
                    if (w.name === "seed") {
                        this.seedWidget = w;
                        this.seedWidget.value = SPECIAL_SEED_RANDOM;
                    } else if (w.name === "control_after_generate") {
                        this.widgets.splice(i, 1);
                    }
                }

                this.addWidget(
                    "button",
                    "🎲 Randomize Each Time",
                    "",
                    () => {
                        this.seedWidget.value = SPECIAL_SEED_RANDOM;
                    },
                    {serialize: false},
                );

                this.addWidget(
                    "button",
                    "🎲 New Fixed Random",
                    "",
                    () => {
                        this.seedWidget.value = this.generateRandomSeed();
                    },
                    {serialize: false},
                );

                this.lastSeedButton = this.addWidget(
                    "button",
                    LAST_SEED_BUTTON_LABEL,
                    "",
                    () => {
                        this.seedWidget.value = this.lastSeed != null ? this.lastSeed : this.seedWidget.value;
                        this.lastSeedButton.name = LAST_SEED_BUTTON_LABEL;
                        this.lastSeedButton.disabled = true;
                    },
                    {width: 50, serialize: false},
                );
                this.lastSeedButton.disabled = true;

                // Hook into queue prompt to handle seed logic
                const self = this;
                const origApply = app.queuePrompt;
                // We can't easily hook app.queuePrompt globally without affecting everything.
                // Instead, we'll listen for the event if possible, or just rely on the fact that
                // we need to update the widget value *before* the graph is serialized.
                // But ComfyUI serializes the graph when you click Queue.
                
                // rgthree uses a custom event "comfy-api-queue-prompt-before".
                // Since we don't have the full rgthree infrastructure, we'll try to hook into the graph serialization
                // or just use the standard onExecute (which is too late for frontend changes to stick).
                
                // A common workaround is to hook into the "graphToPrompt" or similar.
                // Let's try to hook into the api.queuePrompt if we can find where it is exposed, 
                // or just add a listener to the "queue" button if possible.
                
                // Actually, the best way without a framework is to override the widget's serialize method?
                // No, because we need to update other widgets (last seed button).
                
                // Let's try to use the `onSerialize` method of the node.
                this.onSerialize = function(o) {
                    // This is called when saving workflow, but also potentially before queuing?
                    // No, queuing uses `graphToPrompt`.
                };
            };

            nodeType.prototype.generateRandomSeed = function() {
                let step = this.seedWidget.options.step || 1;
                const randomMin = Number(this.properties['randomMin'] || 0);
                const randomMax = Number(this.properties['randomMax'] || 1125899906842624);
                const randomRange = (randomMax - randomMin) / (step / 10);
                let seed = Math.floor(Math.random() * randomRange) * (step / 10) + randomMin;
                if (SPECIAL_SEEDS.includes(seed)) {
                    seed = 0;
                }
                return seed;
            };

            nodeType.prototype.getSeedToUse = function() {
                const inputSeed = Number(this.seedWidget.value);
                let seedToUse = null;

                if (SPECIAL_SEEDS.includes(inputSeed)) {
                    if (typeof this.lastSeed === "number" && !SPECIAL_SEEDS.includes(this.lastSeed)) {
                        if (inputSeed === SPECIAL_SEED_INCREMENT) {
                            seedToUse = this.lastSeed + 1;
                        } else if (inputSeed === SPECIAL_SEED_DECREMENT) {
                            seedToUse = this.lastSeed - 1;
                        }
                    }
                    if (seedToUse == null || SPECIAL_SEEDS.includes(seedToUse)) {
                        seedToUse = this.generateRandomSeed();
                    }
                }
                return seedToUse ?? inputSeed;
            };
            
            // We need to intercept the queue process to update the seed.
            // Since we can't easily modify app.queuePrompt safely from a node definition,
            // we will use a global event listener approach if possible, or monkey patch locally.
            
            // Let's try to monkey patch the api.queuePrompt just once.
            if (!window.ehn_seed_hook_installed) {
                const api = app.api;
                const originalQueuePrompt = api.queuePrompt;
                api.queuePrompt = async function(number, {output, workflow}) {
                    // Find all EHN_Seed nodes and update them
                    if (workflow && workflow.nodes) {
                        for (const node of workflow.nodes) {
                            if (node.type === "EHN_Seed") {
                                const graphNode = app.graph.getNodeById(node.id);
                                if (graphNode) {
                                    const seedToUse = graphNode.getSeedToUse();
                                    
                                    // Update workflow data
                                    const seedWidgetIndex = graphNode.widgets.findIndex(w => w.name === "seed");
                                    if (seedWidgetIndex !== -1) {
                                        node.widgets_values[seedWidgetIndex] = seedToUse;
                                    }
                                    
                                    // Update output data
                                    if (output[node.id] && output[node.id].inputs) {
                                        output[node.id].inputs.seed = seedToUse;
                                    }
                                    
                                    // Update UI
                                    graphNode.lastSeed = seedToUse;
                                    if (seedToUse != graphNode.seedWidget.value) {
                                        graphNode.lastSeedButton.name = `♻️ ${graphNode.lastSeed}`;
                                        graphNode.lastSeedButton.disabled = false;
                                    } else {
                                        graphNode.lastSeedButton.name = LAST_SEED_BUTTON_LABEL;
                                        graphNode.lastSeedButton.disabled = true;
                                    }
                                    if (graphNode.lastSeedValue) {
                                        graphNode.lastSeedValue.value = `Last Seed: ${graphNode.lastSeed}`;
                                    }
                                }
                            }
                        }
                    }
                    return originalQueuePrompt.apply(this, arguments);
                };
                window.ehn_seed_hook_installed = true;
            }

            nodeType.prototype.getExtraMenuOptions = function(canvas, options) {
                options.splice(options.length - 1, 0, {
                    content: "Show/Hide Last Seed Value",
                    callback: (value, options, event, parentMenu, node) => {
                        node.properties["showLastSeed"] = !node.properties["showLastSeed"];
                        if (node.properties["showLastSeed"]) {
                            node.addLastSeedValue();
                        } else {
                            node.removeLastSeedValue();
                        }
                    },
                });
            };

            nodeType.prototype.addLastSeedValue = function() {
                if (this.lastSeedValue) return;
                this.lastSeedValue = ComfyWidgets["STRING"](
                    this,
                    "last_seed",
                    ["STRING", {multiline: true}],
                    app,
                ).widget;
                this.lastSeedValue.inputEl.readOnly = true;
                this.lastSeedValue.inputEl.style.fontSize = "0.75rem";
                this.lastSeedValue.inputEl.style.textAlign = "center";
                this.computeSize();
            };

            nodeType.prototype.removeLastSeedValue = function() {
                if (!this.lastSeedValue) return;
                this.lastSeedValue.inputEl.remove();
                this.widgets.splice(this.widgets.indexOf(this.lastSeedValue), 1);
                this.lastSeedValue = null;
                this.computeSize();
            };
            
            nodeType.prototype.onConfigure = function(info) {
                if (this.properties?.["showLastSeed"]) {
                    this.addLastSeedValue();
                }
            };
        }
    }
});
