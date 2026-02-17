import torch
from diffusers.schedulers.scheduling_flow_match_euler_discrete import FlowMatchEulerDiscreteScheduler
from comfy.samplers import SCHEDULER_HANDLERS, SCHEDULER_NAMES, KSampler

def get_sigmas_sd3(m, s):
    sc = FlowMatchEulerDiscreteScheduler(shift=3.0)
    sc.set_timesteps(s, device="cpu")
    return sc.sigmas

def get_sigmas_flux(m, s):
    sc = FlowMatchEulerDiscreteScheduler(shift=1.0)
    sc.set_timesteps(s, device="cpu")
    return sc.sigmas

if "FlowMatchEulerDiscreteScheduler" not in SCHEDULER_HANDLERS:
    SCHEDULER_HANDLERS["FlowMatchEulerDiscreteScheduler"] = get_sigmas_sd3
    SCHEDULER_NAMES.append("FlowMatchEulerDiscreteScheduler")
    if "FlowMatchEulerDiscreteScheduler" not in KSampler.SCHEDULERS: KSampler.SCHEDULERS.append("FlowMatchEulerDiscreteScheduler")

if "FlowMatchEulerDiscreteScheduler_Flux" not in SCHEDULER_HANDLERS:
    SCHEDULER_HANDLERS["FlowMatchEulerDiscreteScheduler_Flux"] = get_sigmas_flux
    SCHEDULER_NAMES.append("FlowMatchEulerDiscreteScheduler_Flux")
    if "FlowMatchEulerDiscreteScheduler_Flux" not in KSampler.SCHEDULERS: KSampler.SCHEDULERS.append("FlowMatchEulerDiscreteScheduler_Flux")

class EHN_FlowMatchEulerScheduler: pass
