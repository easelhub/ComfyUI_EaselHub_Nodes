import torch
import comfy.samplers

_EHN_SCHEDULER_CONFIG = {"shift": 3.0}

def get_sigmas_flow_match_euler_discrete(n, sigma_min, sigma_max, shift):
    t = torch.linspace(1, 0, n + 1)
    t_shifted = (t * shift) / (1 + (shift - 1) * t)
    return t_shifted * (sigma_max - sigma_min) + sigma_min

if not hasattr(comfy.samplers, "ehn_original_calculate_sigmas"):
    comfy.samplers.ehn_original_calculate_sigmas = comfy.samplers.calculate_sigmas

def ehn_calculate_sigmas(model, scheduler_name, steps):
    if scheduler_name == "FlowMatchEulerDiscrete":
        if hasattr(model, "model") and hasattr(model.model, "model_sampling"):
            ms = model.model.model_sampling
        elif hasattr(model, "model_sampling"):
            ms = model.model_sampling
        else:
            ms = model
            
        shift = _EHN_SCHEDULER_CONFIG["shift"]
        return get_sigmas_flow_match_euler_discrete(steps, ms.sigma_min, ms.sigma_max, shift)
    return comfy.samplers.ehn_original_calculate_sigmas(model, scheduler_name, steps)

comfy.samplers.calculate_sigmas = ehn_calculate_sigmas

if "FlowMatchEulerDiscrete" not in comfy.samplers.SCHEDULER_NAMES:
    comfy.samplers.SCHEDULER_NAMES.append("FlowMatchEulerDiscrete")

class EHN_SchedulerInjector:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "model": ("MODEL",),
                "shift": ("FLOAT", {"default": 3.0, "min": 0.1, "max": 100.0, "step": 0.1}),
            }
        }
    RETURN_TYPES = ("MODEL",)
    FUNCTION = "inject"
    CATEGORY = "EaselHub Nodes/System"

    def inject(self, model, shift):
        _EHN_SCHEDULER_CONFIG["shift"] = shift
        return (model,)