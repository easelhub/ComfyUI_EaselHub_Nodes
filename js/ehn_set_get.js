import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "Comfy.EaselHubNodes.SetGet",
    
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        
        // --- 逻辑 1: EHN_SetVariable (发送端) ---
        if (nodeData.name === "EHN_SetVariable") {
            // 当节点创建时，设置默认颜色方便区分
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                const r = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;
                this.color = "#234d35"; // 暗绿色，代表写入
                this.bgcolor = "#1a3324";
                return r;
            };
            
            // 当变量名修改时，通知更新
            const onConfigure = nodeType.prototype.onConfigure;
            nodeType.prototype.onConfigure = function() {
                const r = onConfigure ? onConfigure.apply(this, arguments) : undefined;
                // 触发一次全局更新
                updateAllGetNodes(app);
                return r;
            };
        }

        // --- 逻辑 2: EHN_GetVariable (接收端) ---
        if (nodeData.name === "EHN_GetVariable") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                const r = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;
                this.color = "#23354d"; // 暗蓝色，代表读取
                this.bgcolor = "#1a2433";
                
                // 只有这一个 widget，保存引用
                this.nameWidget = this.widgets[0];
                
                // 每次点击该节点或鼠标悬停时，尝试刷新列表
                // 这样可以保证用户在操作时列表是最新的
                this.onMouseEnter = function() {
                    updateNodeList(this);
                }
                
                // 初始化时运行一次
                setTimeout(() => updateNodeList(this), 100);
                return r;
            };
        }
    }
});

// --- 核心辅助函数 ---

/**
 * 扫描当前画布，找到所有 EHN_SetVariable 定义的名字
 */
function getAvailableVarNames() {
    const names = new Set();
    const graph = app.graph;
    if (!graph) return [];

    for (const node of graph._nodes) {
        if (node.type === "EHN_SetVariable") {
            // 假设第二个 widget 是 var_name (STRING)
            // 结构: [input_data, var_name]
            const nameWidget = node.widgets && node.widgets.find(w => w.name === "var_name");
            if (nameWidget && nameWidget.value) {
                names.add(nameWidget.value);
            }
        }
    }
    return Array.from(names).sort();
}

/**
 * 更新特定 Get 节点的下拉菜单
 */
function updateNodeList(node) {
    if (!node || node.type !== "EHN_GetVariable") return;
    
    const widget = node.widgets[0];
    if (!widget) return;

    const availableNames = getAvailableVarNames();
    
    if (availableNames.length === 0) {
        widget.options.values = ["(No Vars Found)"];
        return;
    }

    // 更新下拉列表
    widget.options.values = availableNames;

    // 如果当前选中的值不在列表里（比如改名了），重置为第一个
    if (!availableNames.includes(widget.value)) {
        // 尝试保持空或者是第一个
        if (widget.value === "(No Vars Found)" || widget.value === "") {
             widget.value = availableNames[0];
        }
    }
}

/**
 * 更新画布上所有的 Get 节点
 */
function updateAllGetNodes(app) {
    if (!app.graph) return;
    for (const node of app.graph._nodes) {
        if (node.type === "EHN_GetVariable") {
            updateNodeList(node);
        }
    }
}

// 监听画布的通用事件，以便在添加/删除节点时自动刷新
// 这是一个比较激进的监听，为了性能，我们通过 onMouseEnter 辅助
const originalGraphAdd = LGraph.prototype.add;
LGraph.prototype.add = function(node) {
    const r = originalGraphAdd.apply(this, arguments);
    if (node.type === "EHN_SetVariable") {
        setTimeout(() => updateAllGetNodes(app), 100);
    }
    return r;
}