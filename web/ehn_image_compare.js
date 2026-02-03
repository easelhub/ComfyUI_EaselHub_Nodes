import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

app.registerExtension({
    name: "EaselHub.ImageCompare",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "EHN_ImageCompare") {
            nodeType.prototype.onExecuted = function(message) {
                if (message?.comparison_images?.length >= 2) {
                    if (!this.compareWidget) {
                        const c = document.createElement("div");
                        this.compareWidget = this.addDOMWidget("ehn_compare_view", "compare", c, {serialize:false, hideOnZoom:false});
                        Object.assign(c.style, {width:"100%", height:"100%"});
                    }
                    this.updateComparison(message.comparison_images);
                }
            };
            nodeType.prototype.updateComparison = function(images) {
                const w = this.compareWidget;
                if (!w) return;
                const el = w.element;
                el.innerHTML = "";
                const getUrl = i => api.apiURL(`/view?filename=${encodeURIComponent(i.filename)}&type=${i.type}&subfolder=${encodeURIComponent(i.subfolder)}`);
                const uA = getUrl(images[0]), uB = getUrl(images[1]);
                
                const s = document.createElement("style");
                s.textContent = `.ehn-cmp{position:relative;width:100%;height:100%;overflow:hidden;cursor:col-resize;background:#222;display:flex;align-items:center;justify-content:center;border-radius:4px}.ehn-img{position:absolute;top:0;left:0;width:100%;height:100%;object-fit:contain;pointer-events:none;user-select:none}.ehn-line{position:absolute;top:0;bottom:0;width:1px;background:rgba(255,255,255,0.8);pointer-events:none;z-index:20}.ehn-lbl{position:absolute;bottom:5px;padding:2px 6px;background:rgba(0,0,0,0.6);color:white;font:10px sans-serif;border-radius:4px;pointer-events:none;z-index:25}`;
                el.appendChild(s);

                const wrap = document.createElement("div"); wrap.className = "ehn-cmp";
                const mkImg = (src, z) => {const i=document.createElement("img");i.src=src;i.className="ehn-img";i.style.zIndex=z;return i;};
                const imgB = mkImg(uB, "1");
                const imgA = mkImg(uA, "10"); imgA.style.clipPath = "polygon(0 0, 50% 0, 50% 100%, 0 100%)";
                const line = document.createElement("div"); line.className = "ehn-line"; line.style.left = "50%";
                const lbl = (t,p) => {const d=document.createElement("div");d.className="ehn-lbl";d.innerText=t;d.style[p]="5px";return d;};
                
                [imgB, imgA, line, lbl("A","left"), lbl("B","right")].forEach(c => wrap.appendChild(c));

                wrap.onmousemove = e => {
                    const r = wrap.getBoundingClientRect();
                    const p = Math.max(0, Math.min(100, ((e.clientX - r.left)/r.width)*100));
                    imgA.style.clipPath = `polygon(0 0, ${p}% 0, ${p}% 100%, 0 100%)`;
                    line.style.left = `${p}%`;
                };
                el.appendChild(wrap);

                const ti = new Image();
                ti.onload = () => { if(ti.naturalWidth) this.setSize([this.size[0], (this.size[0] * ti.naturalHeight/ti.naturalWidth)+40]); };
                ti.src = uA;
            };
        }
    }
});