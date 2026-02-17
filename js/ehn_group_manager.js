import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "EHN.GroupManager",
    async nodeCreated(node, app) {
        if (node.comfyClass === "EHN_GroupManager") {
            node.widgets = node.widgets || [];
            node.addWidget("button", "REFRESH", null, () => refresh(node));
            
            function refresh(n) {
                const existing = new Set(n.widgets.filter(w => w.type === "toggle").map(w => w.name));
                const groups = app.graph._groups || [];
                
                groups.forEach(g => {
                    const name = g.title || "Group";
                    if (!existing.has(name)) {
                        n.addWidget("toggle", name, true, (v) => {
                            g.recomputeInsideNodes();
                            g._nodes.forEach(xn => {
                                xn.mode = v ? 0 : 2; 
                            });
                        });
                    }
                });

                n.setSize([n.size[0], Math.max(100, n.widgets.length * 20 + 40)]);
                app.graph.setDirtyCanvas(true, true);
            }
            
            refresh(node);
        }
    }
});
