import torch, comfy.model_management as mm
from unittest.mock import patch
from comfy.ldm.flux.layers import timestep_embedding, apply_mod

TC_CFG = {
    "flux": {"c":[498.6,-283.7,55.8,-3.8,0.26], "t":0.4, "r":(0.,1.)},
    "hunyuan_video": {"c":[733.2,-401.1,67.5,-3.1,0.09], "t":0.15, "r":(0.,1.)},
    "ltxv": {"c":[21.4,-12.8,2.3,0.79,0.009], "t":0.06, "r":(0.,1.)},
    "wan2.1_t2v_14B": {"c":[-5784.5,5449.5,-1811.1,256.2,-13.0], "t":0.2, "r":(0.,1.)}
}

class TeaLogic:
    def __init__(self, c, t, dev): self.c=torch.tensor(c,device=dev); self.t=t; self.acc=0.; self.pi=None; self.pr=None
    def check(self, x, en=True):
        if not en: return True, None
        if self.pi is None: self.pi=x; return True, None
        diff = (x - self.pi).abs().mean(); norm = self.pi.abs().mean() + 1e-6
        d = self.c[0]; l1 = diff/norm
        for i in range(1, len(self.c)): d = d * l1 + self.c[i]
        self.acc += d.abs().item(); self.pi = x
        if self.acc < self.t: return False, self.pr
        self.acc = 0.; return True, None
    def update(self, i, o): self.pr = (o - i).detach()

def flux_fw(self, img, img_ids, txt, txt_ids, timesteps, y, guidance=None, control=None, transformer_options={}, attn_mask=None):
    tc = transformer_options.get("teacache_opts", {})
    l = getattr(self, "tc_logic", None)
    img_in = self.img_in(img)
    vec = self.time_in(timestep_embedding(timesteps, 256).to(img.dtype))
    if self.params.guidance_embed and guidance is not None: vec += self.guidance_in(timestep_embedding(guidance, 256).to(img.dtype))
    vec += self.vector_in(y[:,:self.params.vec_in_dim])
    txt_in = self.txt_in(txt)
    pe = self.pe_embedder(torch.cat((txt_ids, img_ids), 1)) if img_ids is not None else None
    
    im1, _ = self.double_blocks[0].img_mod(vec)
    mi = apply_mod(self.double_blocks[0].img_norm1(img_in), (1+im1.scale), im1.shift)
    
    if l is None: l = TeaLogic(tc['c'], tc['t'], img.device); self.tc_logic = l
    run, cache = l.check(mi, tc.get('en', True))
    
    if not run and cache is not None: img_in += cache
    else:
        ori = img_in.clone()
        for i, b in enumerate(self.double_blocks):
            img_in, txt_in = b(img=img_in, txt=txt_in, vec=vec, pe=pe, attn_mask=attn_mask)
            if control and i < len(control.get("input",[])) and control["input"][i] is not None: img_in += control["input"][i]
        cat = torch.cat((txt_in, img_in), 1)
        for i, b in enumerate(self.single_blocks):
            cat = b(cat, vec=vec, pe=pe, attn_mask=attn_mask)
            if control and i < len(control.get("output",[])) and control["output"][i] is not None: cat[:, txt_in.shape[1]:, ...] += control["output"][i]
        img_in = cat[:, txt_in.shape[1]:, ...]
        l.update(ori, img_in)
    return self.final_layer(img_in, vec)

class EHN_TeaCache:
    @classmethod
    def INPUT_TYPES(s): return {"required": {"model":("MODEL",), "model_type":(list(TC_CFG.keys()),), "efficiency_factor":("FLOAT",{"default":1.0})}}
    RETURN_TYPES = ("MODEL",); FUNCTION = "apply"; CATEGORY = "EaselHub/Video"
    def apply(self, model, model_type, efficiency_factor):
        cfg = TC_CFG.get(model_type, TC_CFG["flux"])
        nm = model.clone()
        opts = nm.model_options.setdefault("transformer_options", {})
        opts["teacache_opts"] = {"c":cfg["c"], "t":cfg["t"]*efficiency_factor, "en":False}
        
        dm = nm.get_model_object("diffusion_model")
        fn = flux_fw if "flux" in model_type else None 
        if not fn: return (model,) 

        patcher = patch.multiple(dm, forward_orig=fn.__get__(dm, dm.__class__))
        def wrap(f, kw):
            t, c, o = kw["timestep"], kw["c"], kw["c"]["transformer_options"]
            pct = 0.5
            if (s:=o.get("sample_sigmas")) is not None:
                try: pct = (s==t[0]).nonzero().item() / (len(s)-1)
                except: pass
            o["teacache_opts"]["en"] = (cfg["r"][0] <= pct <= cfg["r"][1])
            if pct<=0.01 or pct>=0.99: 
                if hasattr(dm, "tc_logic"): delattr(dm, "tc_logic")
            with patcher: return f(kw["input"], t, **c)
        nm.set_model_unet_function_wrapper(wrap)
        return (nm,)