import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

app.registerExtension({
    name: "Comfy.EaselHubNodes.SetGet",
    
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        
        // --- Setter Logic ---
        if (nodeData.name === "EHN_SetVariable") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                const r = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;
                this.color = "#234d35"; // Green
                this.bgcolor = "#1a3324";
                return r;
            };
            
            const triggerUpdate = () => {
                if (this._updateTimeout) clearTimeout(this._updateTimeout);
                this._updateTimeout = setTimeout(() => { updateAllGetNodes(app); }, 200);
            };

            const onConfigure = nodeType.prototype.onConfigure;
            nodeType.prototype.onConfigure = function() {
                const r = onConfigure ? onConfigure.apply(this, arguments) : undefined;
                triggerUpdate();
                return r;
            };

            const onWidgetChanged = nodeType.prototype.onWidgetChanged;
            nodeType.prototype.onWidgetChanged = function(name) {
                const r = onWidgetChanged ? onWidgetChanged.apply(this, arguments) : undefined;
                if (name === "var_name") triggerUpdate();
                return r;
            };
        }

        // --- Getter Logic ---
        if (nodeData.name === "EHN_GetVariable") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                const r = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;
                this.color = "#23354d"; // Blue
                this.bgcolor = "#1a2433";
                
                this.onMouseEnter = function() { updateNodeList(this); }
                setTimeout(() => updateNodeList(this), 500);
                return r;
            };
        }
    },

    async setup() {
        api.addEventListener("graph-configured", () => {
            setTimeout(() => updateAllGetNodes(app), 500);
        });
    }
});

function getAvailableVarNames() {
    const names = new Set();
    const graph = app.graph;
    if (!graph) return [];

    for (const node of graph._nodes) {
        if (node.type === "EHN_SetVariable") {
            const w = node.widgets && node.widgets.find(w => w.name === "var_name");
            if (w && w.value && typeof w.value === 'string' && w.value.trim() !== "") {
                names.add(w.value);
            }
        }
    }
    return Array.from(names).sort();
}

function updateNodeList(node) {
    if (!node || node.type !== "EHN_GetVariable") return;
    const widget = node.widgets.find(w => w.name === "var_name") || node.widgets[0];
    if (!widget) return;

    const names = getAvailableVarNames();
    if (names.length === 0) {
        widget.options.values = ["(No Vars Found)"];
        return;
    }

    widget.options.values = names;
    if (widget.value === "(No Vars Found)" || widget.value === "") {
         widget.value = names[0];
    }
}

function updateAllGetNodes(app) {
    if (!app.graph) return;
    for (const node of app.graph._nodes) {
        if (node.type === "EHN_GetVariable") updateNodeList(node);
    }
}

let _addTimeout = null;
const originalGraphAdd = LGraph.prototype.add;
LGraph.prototype.add = function(node) {
    const r = originalGraphAdd.apply(this, arguments);
    if (node.type === "EHN_SetVariable") {
        if (_addTimeout) clearTimeout(_addTimeout);
        _addTimeout = setTimeout(() => updateAllGetNodes(app), 200);
    }
    return r;
}