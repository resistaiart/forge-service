# forge_settings.py
import random
import logging
from typing import Dict, Any, Optional
from enum import Enum

# Set up logging
logger = logging.getLogger(__name__)

# Enums for better type safety
class SamplerType(Enum):
    DPM_PP_2M = "DPM++ 2M Karras"
    EULER_A = "Euler a"
    EULER = "Euler"
    LMS = "LMS"
    DDIM = "DDIM"
    DPM_2 = "DPM2"
    DPM_2_A = "DPM2 a"
    DPM_PP_2S_A = "DPM++ 2S a"

class SchedulerType(Enum):
    KARRAS = "Karras"
    SIMPLE = "Simple"
    NATIVE = "Native"
    EXPONENTIAL = "Exponential"

class GoalType(Enum):
    T2I = "t2i"  # Text-to-Image
    T2V = "t2v"  # Text-to-Video
    I2I = "i2i"  # Image-to-Image
    I2V = "i2v"  # Image-to-Video
    UPSCALE = "upscale"
    INTERROGATE = "interrogate"

# Default settings configuration
_DEFAULT_SETTINGS = {
    GoalType.T2I.value: {
        "checkpoint": "forge-base-v1.safetensors",
        "sampler": SamplerType.DPM_PP_2M.value,
        "steps": 28,
        "cfg_scale": 7.5,
        "resolution": "832x1216",
        "scheduler": SchedulerType.KARRAS.value,
        "denoise": 0.25,
        "batch_size": 1,
        "clip_skip": 2,
        "eta": 0.0,
        "precision": "autocast"
    },
    GoalType.T2V.value: {
        "checkpoint": "forge-animate-v1.safetensors",
        "sampler": SamplerType.DPM_PP_2M.value,
        "steps": 35,
        "cfg_scale": 8.5,
        "resolution": "768x768",
        "scheduler": SchedulerType.KARRAS.value,
        "denoise": 0.25,
        "batch_size": 1,
        "fps": 24,
        "clip_skip": 2,
        "motion_bucket_id": 127,
        "augmentation_level": 0.1
    },
    GoalType.I2I.value: {
        "checkpoint": "forge-base-v1.safetensors",
        "sampler": SamplerType.DPM_PP_2M.value,
        "steps": 30,
        "cfg_scale": 7.0,
        "resolution": "match_input",
        "scheduler": SchedulerType.KARRAS.value,
        "denoise": 0.65,
        "batch_size": 1,
        "clip_skip": 2
    },
    GoalType.I2V.value: {
        "checkpoint": "forge-animate-v1.safetensors",
        "sampler": SamplerType.DPM_PP_2M.value,
        "steps": 40,
        "cfg_scale": 8.0,
        "resolution": "768x768",
        "scheduler": SchedulerType.KARRAS.value,
        "denoise": 0.35,
        "batch_size": 1,
        "fps": 20,
        "clip_skip": 2,
        "motion_bucket_id": 127
    },
    GoalType.UPSCALE.value: {
        "checkpoint": "forge-upscale-v1.safetensors",
        "sampler": SamplerType.EULER_A.value,
        "steps": 20,
        "cfg_scale": 6.0,
        "resolution": "1024x1024",
        "scheduler": SchedulerType.SIMPLE.value,
        "denoise": 0.2,
        "batch_size": 1,
        "clip_skip": 1
    },
    GoalType.INTERROGATE.value: {
        "checkpoint": "forge-base-v1.safetensors",
        "sampler": SamplerType.EULER.value,
        "steps": 15,
        "cfg_scale": 3.0,
        "resolution": "512x512",
        "scheduler": SchedulerType.NATIVE.value,
        "denoise": 0.1,
        "batch_size": 1,
        "clip_skip": 1
    }
}

def build_settings(profile: Optional[Dict[str, Any]] = None, package_goal: str = "t2i") -> Dict[str, Any]:
    if package_goal not in _DEFAULT_SETTINGS:
        logger.warning(f"Unknown goal '{package_goal}', defaulting to 't2i'")
        package_goal = GoalType.T2I.value
    settings = _DEFAULT_SETTINGS[package_goal].copy()
    if profile:
        settings = _apply_profile_settings(settings, profile, package_goal)
    settings["seed"] = random.randint(1, 999999999)
    settings = _validate_and_constrain_settings(settings, package_goal)
    logger.info(f"Built settings for goal '{package_goal}' with seed {settings['seed']}")
    return settings

def _apply_profile_settings(settings: Dict[str, Any], profile: Dict[str, Any], goal: str) -> Dict[str, Any]:
    settings = settings.copy()
    preferred_checkpoint = profile.get("preferred_checkpoint")
    if preferred_checkpoint:
        settings["checkpoint"] = preferred_checkpoint
    preferred_sampler = profile.get("preferred_sampler")
    if preferred_sampler:
        settings["sampler"] = preferred_sampler
    verbosity = profile.get("verbosity", "normal")
    if verbosity == "verbose":
        settings["steps"] += 8
    elif verbosity == "compact":
        settings["steps"] = max(15, settings["steps"] - 5)
    style_boost = profile.get("style_boost", {})
    detected_style = settings.get("detected_style")
    if detected_style and detected_style in style_boost:
        boost = style_boost[detected_style]
        settings["cfg_scale"] += boost.get("cfg_adjust", 0)
        settings["steps"] += boost.get("steps_adjust", 0)
    return settings

def _validate_and_constrain_settings(settings: Dict[str, Any], goal: str) -> Dict[str, Any]:
    settings = settings.copy()
    constraints = {
        "steps": (10, 100),
        "cfg_scale": (1.0, 20.0),
        "denoise": (0.0, 1.0),
        "batch_size": (1, 8),
        "clip_skip": (1, 4),
        "fps": (1, 60),
    }
    for param, (min_val, max_val) in constraints.items():
        if param in settings:
            if param == "denoise":
                settings[param] = max(min_val, min(max_val, settings[param]))
            else:
                settings[param] = int(max(min_val, min(max_val, settings[param])))
    if goal == GoalType.T2V.value or goal == GoalType.I2V.value:
        settings["motion_bucket_id"] = max(1, min(255, settings.get("motion_bucket_id", 127)))
        settings["augmentation_level"] = max(0.0, min(1.0, settings.get("augmentation_level", 0.1)))
    return settings

def get_available_goals() -> list:
    return list(_DEFAULT_SETTINGS.keys())

def get_default_settings(goal: str) -> Dict[str, Any]:
    if goal not in _DEFAULT_SETTINGS:
        raise ValueError(f"Unknown goal: {goal}. Available goals: {list(_DEFAULT_SETTINGS.keys())}")
    return _DEFAULT_SETTINGS[goal].copy()

def explain_settings(settings: Dict[str, Any]) -> Dict[str, str]:
    explanations = {}
    sampler_explanations = {
        SamplerType.DPM_PP_2M.value: "DPM++ 2M Karras: Balanced quality and speed",
        SamplerType.EULER_A.value: "Euler a: Good for creative generations",
        SamplerType.EULER.value: "Euler: Stable and predictable",
        SamplerType.LMS.value: "LMS: Good for detailed outputs",
        SamplerType.DDIM.value: "DDIM: Classic sampler, good for reproducibility"
    }
    if "sampler" in settings:
        explanations["sampler"] = sampler_explanations.get(
            settings["sampler"], f"{settings['sampler']}: Custom sampler choice"
        )
    if "cfg_scale" in settings:
        cfg = settings["cfg_scale"]
        if cfg < 5.0:
            explanations["cfg_scale"] = f"CFG {cfg}: Low guidance, more creative freedom"
        elif cfg < 8.0:
            explanations["cfg_scale"] = f"CFG {cfg}: Balanced guidance and creativity"
        else:
            explanations["cfg_scale"] = f"CFG {cfg}: High guidance, follows prompt closely"
    if "steps" in settings:
        steps = settings["steps"]
        if steps < 20:
            explanations["steps"] = f"{steps} steps: Fast generation, lower detail"
        elif steps < 40:
            explanations["steps"] = f"{steps} steps: Balanced speed and quality"
        else:
            explanations["steps"] = f"{steps} steps: High quality, slower generation"
    return explanations

# === New: API Support Functions ===

def get_defaults() -> Dict[str, str]:
    return {
        "default_prompt": "a blacksmith forging a glowing sword in a fiery workshop, cinematic lighting",
        "default_goal": GoalType.T2I.value
    }

def infer_goal_from_prompt(prompt: str) -> Dict[str, Any]:
    prompt_lower = prompt.lower()
    if any(kw in prompt_lower for kw in ["video", "animation", "frames", "moving", "motion"]):
        goal = GoalType.T2V.value
        confidence = 0.9
    elif any(kw in prompt_lower for kw in ["enhance", "upscale", "sharpen"]):
        goal = GoalType.UPSCALE.value
        confidence = 0.85
    elif any(kw in prompt_lower for kw in ["describe", "what is", "caption", "interrogate"]):
        goal = GoalType.INTERROGATE.value
        confidence = 0.9
    else:
        goal = GoalType.T2I.value
        confidence = 0.7

    return {
        "inferred_goal": goal,
        "confidence": confidence,
        "recommendation": f"Set goal to {goal} for best results."
    }
