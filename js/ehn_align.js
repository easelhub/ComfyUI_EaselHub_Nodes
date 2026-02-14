import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "EHN.Align",
    setup() {
        const orig = LGraphCanvas.prototype.getCanvasMenuOptions;
        LGraphCanvas.prototype.getCanvasMenuOptions = function () {
            const options = orig.apply(this, arguments);
            const selected = Object.values(this.selected_nodes || {});
            if (selected.length < 2) return options;
            options.push(null);
            options.push({
                content: "📏 EHN Align",
                submenu: {
                    options: [
                        { content: "⬆️ Top", callback: () => alignNodes(selected, 'top') },
                        { content: "⬇️ Bottom", callback: () => alignNodes(selected, 'bottom') },
                        { content: "⬅️ Left", callback: () => alignNodes(selected, 'left') },
                        { content: "➡️ Right", callback: () => alignNodes(selected, 'right') },
                        { content: "↔️ Center X", callback: () => alignNodes(selected, 'center_x') },
                        { content: "↕️ Center Y", callback: () => alignNodes(selected, 'center_y') },
                        { content: "🧱 Distribute X", callback: () => alignNodes(selected, 'dist_x') },
                        { content: "☰ Distribute Y", callback: () => alignNodes(selected, 'dist_y') }
                    ]
                }
            });
            return options;
        }
    }
});

function alignNodes(nodes, type) {
    if (nodes.length < 2) return;
    app.graph.beforeChange();
    let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
    for (const n of nodes) {
        if (n.pos[0] < minX) minX = n.pos[0];
        if (n.pos[0] + n.size[0] > maxX) maxX = n.pos[0] + n.size[0];
        if (n.pos[1] < minY) minY = n.pos[1];
        if (n.pos[1] + n.size[1] > maxY) maxY = n.pos[1] + n.size[1];
    }
    if (type === 'top') {
        for (const n of nodes) n.pos[1] = minY;
    } else if (type === 'bottom') {
        for (const n of nodes) n.pos[1] = maxY - n.size[1];
    } else if (type === 'left') {
        for (const n of nodes) n.pos[0] = minX;
    } else if (type === 'right') {
        for (const n of nodes) n.pos[0] = maxX - n.size[0];
    } else if (type === 'center_x') {
        const cx = (minX + maxX) / 2;
        for (const n of nodes) n.pos[0] = cx - n.size[0] / 2;
    } else if (type === 'center_y') {
        const cy = (minY + maxY) / 2;
        for (const n of nodes) n.pos[1] = cy - n.size[1] / 2;
    } else if (type === 'dist_x') {
        nodes.sort((a, b) => a.pos[0] - b.pos[0]);
        let totalW = 0;
        for (const n of nodes) totalW += n.size[0];
        const span = (nodes[nodes.length - 1].pos[0] + nodes[nodes.length - 1].size[0]) - nodes[0].pos[0];
        const gap = (span - totalW) / (nodes.length - 1);
        let cx = nodes[0].pos[0];
        for (let i = 1; i < nodes.length; i++) {
            cx += nodes[i-1].size[0] + gap;
            nodes[i].pos[0] = cx;
        }
    } else if (type === 'dist_y') {
        nodes.sort((a, b) => a.pos[1] - b.pos[1]);
        let totalH = 0;
        for (const n of nodes) totalH += n.size[1];
        const span = (nodes[nodes.length - 1].pos[1] + nodes[nodes.length - 1].size[1]) - nodes[0].pos[1];
        const gap = (span - totalH) / (nodes.length - 1);
        let cy = nodes[0].pos[1];
        for (let i = 1; i < nodes.length; i++) {
            cy += nodes[i-1].size[1] + gap;
            nodes[i].pos[1] = cy;
        }
    }
    for (const n of nodes) n.setDirtyCanvas(true, true);
    app.graph.afterChange();
    app.canvas.setDirty(true, true);
}