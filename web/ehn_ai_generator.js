import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

app.registerExtension({
    name: "EHN.AIGenerator",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "EHN_AIGenerator") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                onNodeCreated?.apply(this, arguments);
                
                const platformWidget = this.widgets.find(w => w.name === "platform");
                const apiKeyWidget = this.widgets.find(w => w.name === "api_key");
                const baseUrlWidget = this.widgets.find(w => w.name === "base_url");
                const modelWidget = this.widgets.find(w => w.name === "model");
                const customModelWidget = this.widgets.find(w => w.name === "custom_model");
                
                const updateVisibility = (platform) => {
                    if (platform === "Custom") {
                        baseUrlWidget.type = "text";
                    } else {
                        baseUrlWidget.type = "hidden";
                    }
                    customModelWidget.type = "text";
                    app.graph.setDirtyCanvas(true, true);
                };

                const updateModels = async (platform) => {
                    if (!platform) return;
                    
                    updateVisibility(platform);

                    apiKeyWidget.value = "";
                    baseUrlWidget.value = "";
                    modelWidget.options.values = [];
                    modelWidget.value = "";

                    try {
                        const configResp = await api.fetchApi("/ehn/get_config", { method: "POST" });
                        if (configResp.ok) {
                            const config = await configResp.json();
                            if (config[platform]) {
                                if (config[platform].api_key) {
                                    apiKeyWidget.value = config[platform].api_key;
                                }
                                if (config[platform].base_url) {
                                    baseUrlWidget.value = config[platform].base_url;
                                }
                                if (config[platform].custom_model) {
                                    customModelWidget.value = config[platform].custom_model;
                                }
                                if (config[platform].models && config[platform].models.length > 0) {
                                    modelWidget.options.values = config[platform].models;
                                    modelWidget.value = config[platform].models[0];
                                }
                            }
                        }
                    } catch (e) {
                        console.error("Failed to fetch config", e);
                    }
                };

                setTimeout(() => {
                    updateModels(platformWidget.value);
                }, 100);

                platformWidget.callback = (value) => {
                    updateModels(value);
                };

                this.addWidget("button", "Update Models", null, () => {
                    const platform = platformWidget.value;
                    const apiKey = apiKeyWidget.value;
                    const baseUrl = baseUrlWidget.value;
                    const customModel = customModelWidget.value;
                    
                    if (!platform || (platform !== "Custom" && !apiKey)) {
                        alert("Please enter Platform and API Key first.");
                        return;
                    }
                    
                    api.fetchApi("/ehn/update_models", {
                        method: "POST",
                        body: JSON.stringify({ platform, api_key: apiKey, base_url: baseUrl, custom_model: customModel }),
                    }).then(async (resp) => {
                        if (resp.ok) {
                            const data = await resp.json();
                            if (data.models && data.models.length > 0) {
                                modelWidget.options.values = data.models;
                                modelWidget.value = data.models[0];
                                alert(`Updated ${data.models.length} models for ${platform}`);
                            } else {
                                alert("No models found.");
                            }
                        } else {
                            alert("Failed to update models: " + resp.statusText);
                        }
                    }).catch(err => {
                        alert("Error: " + err.message);
                    });
                });

            };
        }
    },
});
