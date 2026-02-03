import { app } from "../../scripts/app.js";

const ICONS={left:'<path d="M4 22V2h2v20H4zm4-6h12v-2H8v2zm0-8v2h8V8H8z" fill="currentColor"/>',centerX:'<path d="M11 22v-6H4v-2h7V10H6V8h5V2h2v6h5v2h-5v4h7v2h-7v6h-2z" fill="currentColor"/>',right:'<path d="M20 22V2h-2v20h2zM8 14h8v2H8v-2zm4-6h4v2h-4V8z" fill="currentColor"/>',distX:'<path d="M2 2v20h2V2H2zm18 0v20h2V2h-2zm-8 5h4v10h-4V7z" fill="currentColor"/>',top:'<path d="M2 4h20v2H2V4zm6 4h2v12h-2V8zm8 0h2v8h-2V8z" fill="currentColor"/>',centerY:'<path d="M22 11h-6V4h-2v7H10V6H8v5H2v2h6v5h2v-5h4v7h2v-7h6v-2z" fill="currentColor"/>',bottom:'<path d="M22 20H2v-2h20v2zM8 8h2v8H8V8zm8 4h2v4h-2v-4z" fill="currentColor"/>',distY:'<path d="M22 2H2v2h20V2zM2 20h20v2H2v-2zm5-8v4h10v-4H7z" fill="currentColor"/>'};

app.registerExtension({
    name: "EHN.AlignNodesV1",
    setup() {
        new MutationObserver(() => {
            const toolbox = document.querySelector(".selection-toolbox .p-panel-content");
            if (!toolbox) return;
            const selectedCount = Object.keys(app.canvas.selected_nodes || {}).length;
            const existingGroup = toolbox.querySelector(".ehn-align-group");
            if (selectedCount < 2) {
                if (existingGroup) existingGroup.remove();
                return;
            }
            if (!existingGroup) injectAlignButtons(toolbox);
        }).observe(document.body, { childList: true, subtree: true });
    }
});

function injectAlignButtons(container) {
    const group = document.createElement("div");
    group.className = "ehn-align-group flex flex-row items-center gap-0.5";
    group.style.cssText = "height: 100%; padding-right: calc(var(--spacing) * 1); border-right: 1px solid var(--border-default, #494a50);";
    const bDefs = [{id:"left",t:"Align Left",m:"left"},{id:"centerX",t:"Center X",m:"center_x"},{id:"right",t:"Align Right",m:"right"},{id:"distX",t:"Distribute X",m:"dist_x"},{id:"top",t:"Align Top",m:"top"},{id:"centerY",t:"Center Y",m:"center_y"},{id:"bottom",t:"Align Bottom",m:"bottom"},{id:"distY",t:"Distribute Y",m:"dist_y"}];
    bDefs.forEach(def => {
        const btn = document.createElement("button");
        btn.title = def.t;
        btn.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24">${ICONS[def.id]}</svg>`;
        btn.className = "p-button p-component p-button-text";
        Object.assign(btn.style, {padding: "calc(var(--spacing) * 1.8)", color: "var(--muted-foreground, #8a8a8a)", transition: "background-color 0.2s, color 0.2s"});
        btn.onmouseenter = () => btn.style.backgroundColor = "var(--secondary-background-hover, #313235)";
        btn.onmouseleave = () => btn.style.backgroundColor = "transparent";
        btn.onclick = (e) => {
            e.stopPropagation(); e.preventDefault();
            if (app.canvas.selected_nodes) processAlignment(Object.values(app.canvas.selected_nodes), def.m);
        };
        group.appendChild(btn);
    });
    container.insertBefore(group, container.firstElementChild || null);
}

function processAlignment(nodes, mode) {
    if (nodes.length < 2) return;
    app.graph.change();
    if (mode.startsWith("dist_")) {
        const axis = mode === "dist_x" ? 0 : 1;
        nodes.sort((a, b) => a.pos[axis] - b.pos[axis]);
        const totalSize = nodes.reduce((sum, n) => sum + n.size[axis], 0);
        const range = (nodes[nodes.length - 1].pos[axis] + nodes[nodes.length - 1].size[axis]) - nodes[0].pos[axis];
        const gap = (range - totalSize) / (nodes.length - 1);
        let currentPos = nodes[0].pos[axis];
        nodes.forEach(node => { node.pos[axis] = currentPos; currentPos += node.size[axis] + gap; });
    } else {
        let min = [Infinity, Infinity], max = [-Infinity, -Infinity], center = [0, 0];
        nodes.forEach(n => {
            for (let i = 0; i < 2; i++) {
                if (n.pos[i] < min[i]) min[i] = n.pos[i];
                if (n.pos[i] + n.size[i] > max[i]) max[i] = n.pos[i] + n.size[i];
                center[i] += n.pos[i] + n.size[i] / 2;
            }
        });
        const avg = [center[0] / nodes.length, center[1] / nodes.length];
        nodes.forEach(node => {
            switch (mode) {
                case "left": node.pos[0] = min[0]; break;
                case "right": node.pos[0] = max[0] - node.size[0]; break;
                case "center_x": node.pos[0] = avg[0] - (node.size[0] / 2); break;
                case "top": node.pos[1] = min[1]; break;
                case "bottom": node.pos[1] = max[1] - node.size[1]; break;
                case "center_y": node.pos[1] = avg[1] - (node.size[1] / 2); break;
            }
        });
    }
    app.canvas.setDirty(true, true);
}