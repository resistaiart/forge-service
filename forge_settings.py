### Enhanced `forge_settings.py`
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
    """
    Builds optimized generation settings based on goal type and user profile.
    
    Args:
        profile: User profile containing preferences and settings overrides
        package_goal: The generation goal (t2i, t2v, i2i, i2v, upscale, interrogate)
    
    Returns:
        Dictionary of optimized generation settings with seed
    
    Raises:
        ValueError: If package_goal is not supported
    """
    # Validate goal type
    if package_goal not in _DEFAULT_SETTINGS:
        logger.warning(f"Unknown goal '{package_goal}', defaulting to 't2i'")
        package_goal = GoalType.T2I.value
    
    # Get base settings for the goal
    settings = _DEFAULT_SETTINGS[package_goal].copy()
    
    # Apply profile preferences if available
    if profile:
        settings = _apply_profile_settings(settings, profile, package_goal)
    
    # Add random seed
    settings["seed"] = random.randint(1, 999999999)
    
    # Ensure values are within reasonable bounds
    settings = _validate_and_constrain_settings(settings, package_goal)
    
    logger.info(f"Built settings for goal '{package_goal}' with seed {settings['seed']}")
    return settings

def _apply_profile_settings(settings: Dict[str, Any], profile: Dict[str, Any], goal: str) -> Dict[str, Any]:
    """Apply user profile preferences to settings."""
    settings = settings.copy()
    
    # Apply preferred checkpoint
    preferred_checkpoint = profile.get("preferred_checkpoint")
    if preferred_checkpoint:
        settings["checkpoint"] = preferred_checkpoint
    
    # Apply preferred sampler
    preferred_sampler = profile.get("preferred_sampler")
    if preferred_sampler:
        settings["sampler"] = preferred_sampler
    
    # Apply verbosity adjustments
    verbosity = profile.get("verbosity", "normal")
    if verbosity == "verbose":
        settings["steps"] += 8
    elif verbosity == "compact":
        settings["steps"] = max(15, settings["steps"] - 5)
    
    # Apply style-specific adjustments from profile
    style_boost = profile.get("style_boost", {})
    detected_style = settings.get("detected_style")
    if detected_style and detected_style in style_boost:
        boost = style_boost[detected_style]
        settings["cfg_scale"] += boost.get("cfg_adjust", 0)
        settings["steps"] += boost.get("steps_adjust", 0)
    
    return settings

def _validate_and_constrain_settings(settings: Dict[str, Any], goal: str) -> Dict[str, Any]:
    """Ensure settings are within reasonable bounds."""
    settings = settings.copy()
    
    # Define constraints for different parameters
    constraints = {
        "steps": (10, 100),          # Min, Max steps
        "cfg_scale": (1.0, 20.0),    # Min, Max CFG
        "denoise": (0.0, 1.0),       # Min, Max denoise
        "batch_size": (1, 8),        # Min, Max batch size
        "clip_skip": (1, 4),         # Min, Max clip skip
        "fps": (1, 60),              # Min, Max FPS for video
    }
    
    # Apply constraints
    for param, (min_val, max_val) in constraints.items():
        if param in settings:
            if param == "denoise":
                settings[param] = max(min_val, min(max_val, settings[param]))
            else:
                settings[param] = int(max(min_val, min(max_val, settings[param])))
    
    # Goal-specific constraints
    if goal == GoalType.T2V.value or goal == GoalType.I2V.value:
        settings["motion_bucket_id"] = max(1, min(255, settings.get("motion_bucket_id", 127)))
        settings["augmentation_level"] = max(0.0, min(1.0, settings.get("augmentation_level", 0.1)))
    
    return settings

def get_available_goals() -> list:
    """Get list of available generation goals."""
    return list(_DEFAULT_SETTINGS.keys())

def get_default_settings(goal: str) -> Dict[str, Any]:
    """Get the default settings for a specific goal."""
    if goal not in _DEFAULT_SETTINGS:
        raise ValueError(f"Unknown goal: {goal}. Available goals: {list(_DEFAULT_SETTINGS.keys())}")
    return _DEFAULT_SETTINGS[goal].copy()

def explain_settings(settings: Dict[str, Any]) -> Dict[str, str]:
    """Generate explanations for each setting choice."""
    explanations = {}
    
    # Sampler explanations
    sampler_explanations = {
        SamplerType.DPM_PP_2M.value: "DPM++ 2M Karras: Balanced quality and speed",
        SamplerType.EULER_A.value: "Euler a: Good for creative generations",
        SamplerType.EULER.value: "Euler: Stable and predictable",
        SamplerType.LMS.value: "LMS: Good for detailed outputs",
        SamplerType.DDIM.value: "DDIM: Classic sampler, good for reproducibility"
    }
    
    if "sampler" in settings:
        explanations["sampler"] = sampler_explanations.get(
            settings["sampler"], 
            f"{settings['sampler']}: Custom sampler choice"
        )
    
    # CFG scale explanations
    if "cfg_scale" in settings:
        cfg = settings["cfg_scale"]
        if cfg < 5.0:
            explanations["cfg_scale"] = f"CFG {cfg}: Low guidance, more creative freedom"
        elif cfg < 8.0:
            explanations["cfg_scale"] = f"CFG {cfg}: Balanced guidance and creativity"
        else:
            explanations["cfg_scale"] = f"CFG {cfg}: High guidance, follows prompt closely"
    
    # Steps explanations
    if "steps" in settings:
        steps = settings["steps"]
        if steps < 20:
            explanations["steps"] = f"{steps} steps: Fast generation, lower detail"
        elif steps < 40:
            explanations["steps"] = f"{steps} steps: Balanced speed and quality"
        else:
            explanations["steps"] = f"{steps} steps: High quality, slower generation"
    
    return explanations

# Example usage and testing
if __name__ == "__main__":
    # Test different goals
    test_goals = ["t2i", "t2v", "i2i", "upscale"]
    
    for goal in test_goals:
        print(f"\n=== Settings for {goal} ===")
        settings = build_settings(package_goal=goal)
        
        for key, value in settings.items():
            print(f"  {key}: {value}")
        
        # Show explanations
        explanations = explain_settings(settings)
        print(f"\n  Explanations:")
        for param, explanation in explanations.items():
            print(f"    {param}: {explanation}")
