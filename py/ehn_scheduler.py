import math
import torch
import numpy as np
from diffusers.schedulers.scheduling_flow_match_euler_discrete import FlowMatchEulerDiscreteScheduler
from comfy.samplers import SchedulerHandler, SCHEDULER_HANDLERS, SCHEDULER_NAMES

default_config = {    
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

def flow_match_euler_scheduler_handler(model_sampling, steps):
    scheduler = FlowMatchEulerDiscreteScheduler.from_config(default_config)
    scheduler.set_timesteps(steps, device=model_sampling.device if hasattr(model_sampling, 'device') else 'cpu', mu=0.0)
    sigmas = scheduler.sigmas
    return sigmas

if "FlowMatchEulerDiscreteScheduler" not in SCHEDULER_HANDLERS:
    handler = SchedulerHandler(handler=flow_match_euler_scheduler_handler, use_ms=True)
    SCHEDULER_HANDLERS["FlowMatchEulerDiscreteScheduler"] = handler
    SCHEDULER_NAMES.append("FlowMatchEulerDiscreteScheduler")

try:
    from comfy.samplers import KSampler
    if "FlowMatchEulerDiscreteScheduler" not in KSampler.SCHEDULERS:
        KSampler.SCHEDULERS.append("FlowMatchEulerDiscreteScheduler")
except ImportError:
    pass

class EHN_FlowMatchEulerScheduler:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "steps": ("INT", {"default": 9, "min": 1, "max": 10000}),
                "start_at_step": ("INT", {"default": 0, "min": 0, "max": 10000}),
                "end_at_step": ("INT", {"default": 9999, "min": 0, "max": 10000}),
                "base_image_seq_len": ("INT", {"default": 256}),
                "base_shift": ("FLOAT", {"default": 0.5, "step": 0.01}),
                "invert_sigmas": (["disable", "enable"], {"default": "disable"}),
                "max_image_seq_len": ("INT", {"default": 8192}),
                "max_shift": ("FLOAT", {"default": 1.15, "step": 0.01}),
                "num_train_timesteps": ("INT", {"default": 1000}),
                "shift": ("FLOAT", {"default": 3.0, "step": 0.01}),
                "shift_terminal": ("FLOAT", {"default": 0.0, "step": 0.01}),
                "stochastic_sampling": (["disable", "enable"], {"default": "disable"}),
                "time_shift_type": (["exponential", "linear"], {"default": "exponential"}),
                "use_beta_sigmas": (["disable", "enable"], {"default": "disable"}),
                "use_dynamic_shifting": (["disable", "enable"], {"default": "disable"}),
                "use_exponential_sigmas": (["disable", "enable"], {"default": "disable"}),
                "use_karras_sigmas": (["disable", "enable"], {"default": "disable"}),
                "device": (["auto", "cuda", "cpu"], {"default": "auto"}),
            }
        }

    RETURN_TYPES = ("SIGMAS",)
    RETURN_NAMES = ("sigmas",)
    FUNCTION = "create"
    CATEGORY = "EaselHub/Scheduler"

    def create(self, steps, start_at_step, end_at_step, base_image_seq_len, base_shift, invert_sigmas, max_image_seq_len, max_shift, num_train_timesteps, shift, shift_terminal, stochastic_sampling, time_shift_type, use_beta_sigmas, use_dynamic_shifting, use_exponential_sigmas, use_karras_sigmas, device="auto"):
        config = {
            "base_image_seq_len": base_image_seq_len,
            "base_shift": base_shift,
            "invert_sigmas": invert_sigmas == "enable",
            "max_image_seq_len": max_image_seq_len,
            "max_shift": max_shift,
            "num_train_timesteps": num_train_timesteps,
            "shift": shift,
            "shift_terminal": shift_terminal if shift_terminal != 0.0 else None,
            "stochastic_sampling": stochastic_sampling == "enable",
            "time_shift_type": time_shift_type,
            "use_beta_sigmas": use_beta_sigmas == "enable",
            "use_dynamic_shifting": use_dynamic_shifting == "enable",
            "use_exponential_sigmas": use_exponential_sigmas == "enable",
            "use_karras_sigmas": use_karras_sigmas == "enable",
        }

        scheduler = FlowMatchEulerDiscreteScheduler.from_config(config)
        
        if device == "auto":
            target_device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            target_device = device
        
        scheduler.set_timesteps(steps, device=target_device, mu=0.0)
        sigmas = scheduler.sigmas
        
        end_index = min(end_at_step + 1, len(sigmas))
        sigmas_sliced = sigmas[start_at_step:end_index]
        
        if sigmas_sliced.numel() == 0:
            sigmas_sliced = sigmas
            
        return (sigmas_sliced,)
