import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "EHN.GroupManager",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "EHN_GroupManager") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                if (onNodeCreated) onNodeCreated.apply(this, arguments);
                this.addWidget("button", "REFRESH", null, () => this.sync());
                this.syncInterval = setInterval(() => { if (app.graph) this.sync(); }, 1000);
            };
            const onRemoved = nodeType.prototype.onRemoved;
            nodeType.prototype.onRemoved = function() {
                if (onRemoved) onRemoved.apply(this, arguments);
                if (this.syncInterval) { clearInterval(this.syncInterval); this.syncInterval = null; }
            };
            nodeType.prototype.sync = function() {
                if (!app.graph) return;
                const groups = app.graph._groups || [];
                const gMap = new Map();
                groups.forEach((g, i) => gMap.set(g.title || `Group #${i + 1}`, g));
                if (!this.widgets) this.widgets = [];
                let changed = false;
                const valid = new Set();
                for (let i = this.widgets.length - 1; i >= 0; i--) {
                    const w = this.widgets[i];
                    if (w.type === "button") continue;
                    if (!gMap.has(w.name)) {
                        this.widgets.splice(i, 1);
                        changed = true;
                    } else {
                        valid.add(w.name);
                        const g = gMap.get(w.name);
                        g.recomputeInsideNodes();
                        const active = g._nodes.length > 0 ? g._nodes.some(n => n.mode === 0) : true;
                        if (w.value !== active) {
                            w.value = active;
                        }
                    }
                }
                for (const [t, g] of gMap) {
                    if (valid.has(t)) continue;
                    g.recomputeInsideNodes();
                    const active = g._nodes.length > 0 ? g._nodes.some(n => n.mode === 0) : true;
                    this.addWidget("toggle", t, active, (v) => {
                        const grp = app.graph._groups.find((x, i) => (x.title || `Group #${i + 1}`) === t);
                        if (grp) {
                            grp.recomputeInsideNodes();
                            grp._nodes.forEach(n => n.mode = v ? 0 : 2);
                            app.graph.setDirtyCanvas(true, true);
                        }
                    });
                    changed = true;
                }
                if (changed) {
                    this.setSize([this.size[0], Math.max(100, this.widgets.length * 20 + 50)]);
                    app.graph.setDirtyCanvas(true, true);
                }
            };
        }
    }
});
