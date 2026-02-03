import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

app.registerExtension({
    name: "Comfy.EaselHubNodes.SetGet",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "EHN_SetVariable") {
            nodeType.prototype.onNodeCreated = function () {
                this.color = "#234d35"; this.bgcolor = "#1a3324";
            };
            const update = () => { clearTimeout(this._tm); this._tm = setTimeout(() => updateAllGet(app), 200); };
            const onCfg = nodeType.prototype.onConfigure;
            nodeType.prototype.onConfigure = function() { onCfg?.apply(this,arguments); update(); };
            const onWg = nodeType.prototype.onWidgetChanged;
            nodeType.prototype.onWidgetChanged = function(n) { onWg?.apply(this,arguments); if(n==="var_name") update(); };
        }
        if (nodeData.name === "EHN_GetVariable") {
            nodeType.prototype.onNodeCreated = function () {
                this.color = "#23354d"; this.bgcolor = "#1a2433";
                this.onMouseEnter = () => updateList(this);
                setTimeout(() => updateList(this), 500);
            };
        }
    },
    async setup() { api.addEventListener("graph-configured", () => setTimeout(() => updateAllGet(app), 500)); }
});

function getVars() {
    const s = new Set();
    app.graph?._nodes.forEach(n => {
        if (n.type === "EHN_SetVariable") {
            const v = n.widgets?.find(w => w.name === "var_name")?.value;
            if (v && v.trim()) s.add(v);
        }
    });
    return Array.from(s).sort();
}
function updateList(n) {
    if (n?.type !== "EHN_GetVariable") return;
    const w = n.widgets.find(x => x.name === "var_name") || n.widgets[0];
    if (!w) return;
    const v = getVars();
    w.options.values = v.length ? v : ["(No Vars Found)"];
    if (w.value === "" || w.value === "(No Vars Found)") w.value = w.options.values[0];
}
function updateAllGet(app) { app.graph?._nodes.forEach(n => updateList(n)); }
let _at=null; const oa=LGraph.prototype.add;
LGraph.prototype.add = function(n) {
    const r=oa.apply(this,arguments);
    if(n.type==="EHN_SetVariable") { clearTimeout(_at); _at=setTimeout(()=>updateAllGet(app),200); }
    return r;
};