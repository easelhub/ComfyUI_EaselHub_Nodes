import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "EHN.GroupManager",
    async nodeCreated(node, app) {
        if (node.comfyClass === "EHN_GroupManager") {
            node.widgets = node.widgets || [];
            node.addWidget("button", "REFRESH", null, () => refresh(node));
            
            function refresh(n) {
                if (!app.graph) return;
                const groups = app.graph._groups || [];
                const gMap = new Map(groups.map(g => [g.title || "Group", g]));
                
                // Remove invalid widgets
                for (let i = n.widgets.length - 1; i >= 0; i--) {
                    const w = n.widgets[i];
                    if (w.type === "toggle" && !gMap.has(w.name)) {
                        n.widgets.splice(i, 1);
                    }
                }
                
                // Add or update widgets
                groups.forEach(g => {
                    const name = g.title || "Group";
                    g.recomputeInsideNodes();
                    const active = g._nodes.length > 0 ? g._nodes.some(xn => xn.mode === 0) : true;
                    
                    const existing = n.widgets.find(w => w.name === name && w.type === "toggle");
                    if (existing) {
                        if (existing.value !== active) existing.value = active;
                    } else {
                        n.addWidget("toggle", name, active, (v) => {
                            g.recomputeInsideNodes();
                            g._nodes.forEach(xn => { xn.mode = v ? 0 : 2; });
                        });
                    }
                });
                
                n.setSize([n.size[0], Math.max(100, n.widgets.length * 20 + 40)]);
                app.graph.setDirtyCanvas(true, true);
            }

            setTimeout(() => refresh(node), 100);
        }
    }
});
