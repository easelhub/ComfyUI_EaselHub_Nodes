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
                const modelWidget = this.widgets.find(w => w.name === "model");
                
                const updateModels = async (platform) => {
                    if (!platform) return;
                    apiKeyWidget.value = "";
                    modelWidget.options.values = [];
                    modelWidget.value = "";
                    try {
                        const configResp = await api.fetchApi("/ehn/get_config", { method: "POST" });
                        if (configResp.ok) {
                            const config = await configResp.json();
                            if (config[platform]) {
                                if (config[platform].api_key) apiKeyWidget.value = config[platform].api_key;
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
                    if (!platform || !apiKey) {
                        alert("Please enter Platform and API Key first.");
                        return;
                    }
                    api.fetchApi("/ehn/update_models", {
                        method: "POST",
                        body: JSON.stringify({ platform, api_key: apiKey }),
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
        } else if (nodeData.name === "EHN_OpenAIGenerator") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                onNodeCreated?.apply(this, arguments);
                const apiKeyWidget = this.widgets.find(w => w.name === "api_key");
                const baseUrlWidget = this.widgets.find(w => w.name === "base_url");
                const modelWidget = this.widgets.find(w => w.name === "model");
                const customModelWidget = this.widgets.find(w => w.name === "custom_model");
                
                const updateModels = async () => {
                    try {
                        const configResp = await api.fetchApi("/ehn/get_config", { method: "POST" });
                        if (configResp.ok) {
                            const config = await configResp.json();
                            if (config["OpenAI"]) {
                                if (config["OpenAI"].api_key) apiKeyWidget.value = config["OpenAI"].api_key;
                                if (config["OpenAI"].base_url) baseUrlWidget.value = config["OpenAI"].base_url;
                                if (config["OpenAI"].custom_model) customModelWidget.value = config["OpenAI"].custom_model;
                                if (config["OpenAI"].models && config["OpenAI"].models.length > 0) {
                                    modelWidget.options.values = config["OpenAI"].models;
                                    modelWidget.value = config["OpenAI"].models[0];
                                }
                            }
                        }
                    } catch (e) {
                        console.error("Failed to fetch config", e);
                    }
                };
                setTimeout(() => {
                    updateModels();
                }, 100);

                this.addWidget("button", "Update Models", null, () => {
                    const apiKey = apiKeyWidget.value;
                    const baseUrl = baseUrlWidget.value;
                    const customModel = customModelWidget.value;
                    
                    if (!apiKey) {
                        alert("Please enter API Key first.");
                        return;
                    }
                    
                    api.fetchApi("/ehn/update_models", {
                        method: "POST",
                        body: JSON.stringify({ platform: "OpenAI", api_key: apiKey, base_url: baseUrl, custom_model: customModel }),
                    }).then(async (resp) => {
                        if (resp.ok) {
                            const data = await resp.json();
                            if (data.models && data.models.length > 0) {
                                modelWidget.options.values = data.models;
                                modelWidget.value = data.models[0];
                                alert(`Updated ${data.models.length} models for OpenAI`);
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
        } else if (nodeData.name === "EHN_OllamaGenerator") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                onNodeCreated?.apply(this, arguments);
                const baseUrlWidget = this.widgets.find(w => w.name === "base_url");
                const modelWidget = this.widgets.find(w => w.name === "model");
                const customModelWidget = this.widgets.find(w => w.name === "custom_model");
                
                const updateModels = async () => {
                    try {
                        const configResp = await api.fetchApi("/ehn/get_config", { method: "POST" });
                        if (configResp.ok) {
                            const config = await configResp.json();
                            if (config["Ollama"]) {
                                if (config["Ollama"].base_url) baseUrlWidget.value = config["Ollama"].base_url;
                                if (config["Ollama"].custom_model) customModelWidget.value = config["Ollama"].custom_model;
                                if (config["Ollama"].models && config["Ollama"].models.length > 0) {
                                    modelWidget.options.values = config["Ollama"].models;
                                    modelWidget.value = config["Ollama"].models[0];
                                }
                            }
                        }
                    } catch (e) {
                        console.error("Failed to fetch config", e);
                    }
                };
                setTimeout(() => {
                    updateModels();
                }, 100);

                this.addWidget("button", "Update Models", null, () => {
                    const baseUrl = baseUrlWidget.value;
                    const customModel = customModelWidget.value;
                    
                    api.fetchApi("/ehn/update_models", {
                        method: "POST",
                        body: JSON.stringify({ platform: "Ollama", base_url: baseUrl, custom_model: customModel }),
                    }).then(async (resp) => {
                        if (resp.ok) {
                            const data = await resp.json();
                            if (data.models && data.models.length > 0) {
                                modelWidget.options.values = data.models;
                                modelWidget.value = data.models[0];
                                alert(`Updated ${data.models.length} models for Ollama`);
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
