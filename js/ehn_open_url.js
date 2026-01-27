import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "Comfy.EaselHubNodes.OpenURL",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        const urlMap = {
            "EHN_SiliconFlow": { url: "https://cloud.siliconflow.cn/", text: "🌐 Open SiliconFlow" },
            "EHN_OpenRouter": { url: "https://openrouter.ai/", text: "🌐 Open OpenRouter" },
            "EHN_DeepSeek": { url: "https://platform.deepseek.com/", text: "🌐 Open DeepSeek" },
            "EHN_OpenAI": { url: "https://platform.openai.com/", text: "🌐 Open OpenAI" },
            "EHN_Gemini": { url: "https://aistudio.google.com/", text: "🌐 Open Google AI Studio" }
        };
        if (urlMap[nodeData.name]) {
            const onCr = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                onCr?.apply(this, arguments);
                this.addWidget("button", urlMap[nodeData.name].text, null, () => window.open(urlMap[nodeData.name].url, "_blank"));
            };
        }
    }
});