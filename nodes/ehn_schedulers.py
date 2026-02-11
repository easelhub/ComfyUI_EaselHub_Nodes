import math
import torch
import numpy as np
from comfy.samplers import SchedulerHandler, SCHEDULER_HANDLERS, SCHEDULER_NAMES

try:
    from diffusers.schedulers.scheduling_flow_match_euler_discrete import FlowMatchEulerDiscreteScheduler
except ImportError:
    FlowMatchEulerDiscreteScheduler = None

if FlowMatchEulerDiscreteScheduler:
    _CONFIG = {
        "base_image_seq_len": 256,
        "base_shift": math.log(3),
        "invert_sigmas": False,
        "max_image_seq_len": 8192,
        "max_shift": math.log(3),
        "num_train_timesteps": 1000,
        "shift": 1.0,
        "shift_terminal": None,
        "stochastic_sampling": False,
        "time_shift_type": "exponential",
        "use_beta_sigmas": False,
        "use_dynamic_shifting": True,
        "use_exponential_sigmas": False,
        "use_karras_sigmas": False,
    }

    def _handler(model_sampling, steps):
        s = FlowMatchEulerDiscreteScheduler.from_config(_CONFIG)
        d = model_sampling.device if hasattr(model_sampling, 'device') else 'cpu'
        s.set_timesteps(steps, device=d, mu=0.0)
        return s.sigmas

    if "FlowMatchEulerDiscreteScheduler" not in SCHEDULER_HANDLERS:
        SCHEDULER_HANDLERS["FlowMatchEulerDiscreteScheduler"] = SchedulerHandler(handler=_handler, use_ms=True)
        SCHEDULER_NAMES.append("FlowMatchEulerDiscreteScheduler")

    try:
        from comfy.samplers import KSampler
        if "FlowMatchEulerDiscreteScheduler" not in KSampler.SCHEDULERS:
            KSampler.SCHEDULERS.append("FlowMatchEulerDiscreteScheduler")
    except:
        pass
