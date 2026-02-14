import math, torch
from diffusers.schedulers.scheduling_flow_match_euler_discrete import FlowMatchEulerDiscreteScheduler
from comfy.samplers import SchedulerHandler, SCHEDULER_HANDLERS, SCHEDULER_NAMES, KSampler

class EHN_FlowMatchEulerScheduler:
    CATEGORY, RETURN_TYPES, RETURN_NAMES, FUNCTION = "EaselHub/Scheduler", ("SIGMAS",), ("sigmas",), "create"
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "steps": ("INT", {"default": 20, "min": 1, "max": 10000}),
            "start_at_step": ("INT", {"default": 0, "min": 0, "max": 10000}),
            "end_at_step": ("INT", {"default": 10000, "min": 0, "max": 10000}),
            "shift": ("FLOAT", {"default": 3.0, "step": 0.01}),
            "base_shift": ("FLOAT", {"default": 0.5, "step": 0.01}),
            "max_shift": ("FLOAT", {"default": 1.15, "step": 0.01}),
            "device": (["auto", "cuda", "cpu"], {"default": "auto"})
        }}
    def create(self, steps, start_at_step, end_at_step, shift, base_shift, max_shift, device="auto"):
        dev = "cuda" if device == "auto" and torch.cuda.is_available() else "cpu" if device == "auto" else device
        s = FlowMatchEulerDiscreteScheduler(shift=shift, base_shift=base_shift, max_shift=max_shift)
        s.set_timesteps(steps, device=dev)
        return (s.sigmas[start_at_step:min(end_at_step + 1, len(s.sigmas))],)

if "FlowMatchEulerDiscreteScheduler" not in SCHEDULER_HANDLERS:
    SCHEDULER_HANDLERS["FlowMatchEulerDiscreteScheduler"] = SchedulerHandler(lambda m, s: FlowMatchEulerDiscreteScheduler().set_timesteps(s, device=m.device).sigmas, use_ms=True)
    SCHEDULER_NAMES.append("FlowMatchEulerDiscreteScheduler")
    if "FlowMatchEulerDiscreteScheduler" not in KSampler.SCHEDULERS: KSampler.SCHEDULERS.append("FlowMatchEulerDiscreteScheduler")
