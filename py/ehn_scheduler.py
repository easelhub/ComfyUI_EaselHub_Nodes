import torch
from diffusers.schedulers.scheduling_flow_match_euler_discrete import FlowMatchEulerDiscreteScheduler
from comfy.samplers import SCHEDULER_HANDLERS, SCHEDULER_NAMES, KSampler, SchedulerHandler

def get_sigmas(m, s):
    sc = FlowMatchEulerDiscreteScheduler(shift=1.0)
    sc.set_timesteps(s, device="cpu")
    return sc.sigmas

if "FlowMatchEulerDiscreteScheduler" not in SCHEDULER_HANDLERS:
    SCHEDULER_HANDLERS["FlowMatchEulerDiscreteScheduler"] = SchedulerHandler(get_sigmas)
    SCHEDULER_NAMES.append("FlowMatchEulerDiscreteScheduler")
    if "FlowMatchEulerDiscreteScheduler" not in KSampler.SCHEDULERS: KSampler.SCHEDULERS.append("FlowMatchEulerDiscreteScheduler")

class EHN_FlowMatchEulerScheduler: pass
