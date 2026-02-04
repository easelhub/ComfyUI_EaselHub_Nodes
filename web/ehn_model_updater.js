import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

app.registerExtension({
    name: "Comfy.EaselHubNodes.ModelUpdater",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (["EHN_OpenAI", "EHN_Gemini", "EHN_DeepSeek", "EHN_OpenRouter", "EHN_SiliconFlow"].includes(nodeData.name)) {
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                if (onNodeCreated) onNodeCreated.apply(this, arguments);
                const btn = this.addWidget("button", "🔄 Fetch & Update Models", null, () => {
                    const apiKeyWidget = this.widgets.find(w => w.name === "api_key");
                    const baseUrlWidget = this.widgets.find(w => w.name === "base_url");
                    const providerMap = {
                        "EHN_OpenAI": "openai",
                        "EHN_Gemini": "gemini",
                        "EHN_DeepSeek": "deepseek",
                        "EHN_OpenRouter": "openrouter",
                        "EHN_SiliconFlow": "siliconflow"
                    };
                    const provider = providerMap[nodeData.name];
                    const baseUrl = baseUrlWidget ? baseUrlWidget.value : null;
                    btn.disabled = true;
                    btn.name = "Fetching...";
                    api.fetchApi("/ehn/update_models", {
                        method: "POST",
                        body: JSON.stringify({ provider, api_key: apiKeyWidget ? apiKeyWidget.value : "", base_url: baseUrl }),
                    }).then(async (resp) => {
                        if (resp.status !== 200) {
                            const err = await resp.json();
                            alert("Error: " + (err.error || resp.statusText));
                            return;
                        }
                        const data = await resp.json();
                        if (data.models && data.models.length > 0) {
                            const modelWidget = this.widgets.find(w => w.name === "model");
                            if (modelWidget) {
                                modelWidget.options.values = data.models;
                                modelWidget.value = data.models[0];
                            }
                            alert(`Fetched ${data.models.length} models for ${provider}.`);
                        } else {
                            alert("No models found.");
                        }
                    }).catch(e => alert(e)).finally(() => {
                        btn.disabled = false;
                        btn.name = "🔄 Fetch & Update Models";
                    });
                });
            };
        }
    }
});
