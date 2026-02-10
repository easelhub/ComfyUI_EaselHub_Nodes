import torch
import comfy.samplers

def get_sigmas_flow_match_euler_discrete(n, sigma_min, sigma_max, shift=3.0):
    t = torch.linspace(1, 0, n + 1)
    t_shifted = (t * shift) / (1 + (shift - 1) * t)
    sigmas = t_shifted * (sigma_max - sigma_min) + sigma_min
    return sigmas

if "FlowMatchEulerDiscrete" not in comfy.samplers.SCHEDULER_NAMES:
    comfy.samplers.SCHEDULER_NAMES.append("FlowMatchEulerDiscrete")

original_calculate_sigmas = comfy.samplers.calculate_sigmas

def new_calculate_sigmas(model, scheduler_name, steps):
    if scheduler_name == "FlowMatchEulerDiscrete":
        if hasattr(model, "model") and hasattr(model.model, "model_sampling"): ms = model.model.model_sampling
        elif hasattr(model, "model_sampling"): ms = model.model_sampling
        else: ms = model
        return get_sigmas_flow_match_euler_discrete(steps, ms.sigma_min, ms.sigma_max, shift=3.0)
    return original_calculate_sigmas(model, scheduler_name, steps)

comfy.samplers.calculate_sigmas = new_calculate_sigmas

class EHN_SchedulerInjector:
    @classmethod
    def INPUT_TYPES(s): return {"required": {}}
    RETURN_TYPES = ()
    FUNCTION = "execute"
    CATEGORY = "EaselHub Nodes/System"
    def execute(self): return ()

print("\033[34mComfyUI EaselHub Nodes: \033[92mRegistered FlowMatchEulerDiscrete Scheduler\033[0m")