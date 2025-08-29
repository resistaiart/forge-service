# forge_workflows.py
import random
import re
from typing import Dict, List, Optional, Any

# Use absolute imports (no dots)
from forge_prompts import clean_prompt, analyze_prompt_intent, weight_keywords

# Video-specific configuration
VIDEO_MODELS = {
    "svd": "stabilityai/stable-video-diffusion-img2vid-xt",
    "svd_xt": "stabilityai/stable-video-diffusion-img2vid-xt-1-1",
    "animatediff": "AnimateDiff",
}

def optimise_i2i_package(
    prompt: str, 
    input_image: str, 
    denoise_strength: float = 0.75,
    resources: Optional[List[str]] = None,
    caption: Optional[str] = None
) -> Dict[str, Any]:
    """
    Optimize a package for Image-to-Image generation.
    """
    # Clean and analyze the prompt
    base_prompt = clean_prompt(prompt)
    intent = analyze_prompt_intent(base_prompt)
    weighted_prompt = weight_keywords(base_prompt, intent)
    
    # Get base settings and adapt for I2I
    base_settings = _get_base_settings("i2i", intent)
    base_settings["denoise"] = max(0.1, min(1.0, denoise_strength))
    
    # Generate context-aware negative prompt
    negative_prompt = _get_negative_prompt(intent)
    
    # Build diagnostics
    diagnostics = _generate_diagnostics(base_settings, intent, "i2i")
    diagnostics["denoise_reason"] = f"Denoise {denoise_strength} for {'strong' if denoise_strength > 0.6 else 'moderate'} transformation"
    
    # Build final package
    package = {
        "goal": "i2i",
        "input_image": input_image,
        "original_prompt": prompt,
        "optimized_prompt": weighted_prompt,
        "negative_prompt": negative_prompt,
        "settings": base_settings,
        "resources": resources or [],
        "caption": caption,
        "diagnostics": diagnostics,
        "intent_analysis": intent,
        "workflow_type": "image_to_image"
    }
    
    return package

def optimise_t2v_package(
    prompt: str,
    num_frames: int = 25,
    fps: int = 6,
    motion_intensity: str = "medium",
    resources: Optional[List[str]] = None,
    caption: Optional[str] = None
) -> Dict[str, Any]:
    """
    Optimize a package for Text-to-Video generation.
    """
    # Clean and analyze the prompt
    base_prompt = clean_prompt(prompt)
    intent = analyze_prompt_intent(base_prompt)
    weighted_prompt = _adapt_prompt_for_video(base_prompt, intent)
    
    # Get video-specific settings
    settings = _get_video_settings(intent, num_frames, fps, motion_intensity)
    
    # Video-specific negative prompt
    negative_prompt = _get_video_negative_prompt(intent)
    
    # Build diagnostics
    diagnostics = _generate_video_diagnostics(settings, intent)
    
    # Build final package
    package = {
        "goal": "t2v",
        "original_prompt": prompt,
        "optimized_prompt": weighted_prompt,
        "negative_prompt": negative_prompt,
        "settings": settings,
        "resources": resources or [],
        "caption": caption,
        "diagnostics": diagnostics,
        "intent_analysis": intent,
        "workflow_type": "text_to_video",
        "video_metadata": {
            "num_frames": num_frames,
            "fps": fps,
            "duration_seconds": num_frames / fps if fps > 0 else 0
        }
    }
    
    return package

def optimise_i2v_package(
    prompt: str,
    input_image: str,
    num_frames: int = 25,
    fps: int = 6,
    motion_intensity: str = "medium",
    denoise_strength: float = 0.5,
    resources: Optional[List[str]] = None,
    caption: Optional[str] = None
) -> Dict[str, Any]:
    """
    Optimize a package for Image-to-Video generation.
    """
    # Clean and analyze the prompt
    base_prompt = clean_prompt(prompt)
    intent = analyze_prompt_intent(base_prompt)
    weighted_prompt = _adapt_prompt_for_video(base_prompt, intent)
    
    # Get video-specific settings
    settings = _get_video_settings(intent, num_frames, fps, motion_intensity)
    settings["denoise"] = max(0.1, min(1.0, denoise_strength))
    settings["model"] = VIDEO_MODELS["svd"]
    
    # Video-specific negative prompt
    negative_prompt = _get_video_negative_prompt(intent)
    
    # Build diagnostics
    diagnostics = _generate_video_diagnostics(settings, intent)
    diagnostics["denoise_reason"] = f"Denoise {denoise_strength} for video animation from image"
    
    # Build final package
    package = {
        "goal": "i2v",
        "input_image": input_image,
        "original_prompt": prompt,
        "optimized_prompt": weighted_prompt,
        "negative_prompt": negative_prompt,
        "settings": settings,
        "resources": resources or [],
        "caption": caption,
        "diagnostics": diagnostics,
        "intent_analysis": intent,
        "workflow_type": "image_to_video",
        "video_metadata": {
            "num_frames": num_frames,
            "fps": fps,
            "duration_seconds": num_frames / fps if fps > 0 else 0
        }
    }
    
    return package

# Helper functions for video processing
def _adapt_prompt_for_video(prompt: str, intent: Dict[str, str]) -> str:
    """
    Adapt a prompt for video generation by adding motion cues.
    """
    motion_keywords = {
        "low": ["subtle movement", "gentle motion", "slow pan"],
        "medium": ["dynamic", "moving", "panning", "animated"],
        "high": ["rapid motion", "fast movement", "action sequence", "explosion"]
    }
    
    # Add motion cues based on intent
    prompt_lower = prompt.lower()
    weighted_prompt = weight_keywords(prompt, intent)
    
    # Check if motion is already described
    motion_words = ["moving", "motion", "pan", "zoom", "rotate", "animate"]
    has_motion = any(word in prompt_lower for word in motion_words)
    
    if not has_motion:
        # Add appropriate motion description
        motion_level = "medium"
        motion_desc = motion_keywords[motion_level][0]
        weighted_prompt = f"{weighted_prompt}, {motion_desc}"
    
    return weighted_prompt

def _get_video_settings(
    intent: Dict[str, str], 
    num_frames: int, 
    fps: int, 
    motion_intensity: str
) -> Dict[str, Any]:
    """
    Get video-specific generation settings.
    """
    motion_bucket_map = {
        "low": 80,
        "medium": 127,
        "high": 180
    }
    
    augmentation_map = {
        "low": 0.0,
        "medium": 0.1,
        "high": 0.3
    }
    
    return {
        "model": VIDEO_MODELS["svd_xt"],
        "num_frames": max(14, min(100, num_frames)),
        "fps": max(1, min(30, fps)),
        "motion_bucket_id": motion_bucket_map.get(motion_intensity, 127),
        "augmentation_level": augmentation_map.get(motion_intensity, 0.1),
        "cfg_scale": 3.5,
        "steps": 25,
        "sampler": "Euler",
        "scheduler": "Simple"
    }

def _get_video_negative_prompt(intent: Dict[str, str]) -> str:
    """
    Get video-specific negative prompts.
    """
    base_negative = (
        "blurry, low quality, watermark, artifacts, "
        "bad anatomy, distorted, deformed, ugly, disfigured, "
        "jittery, flickering, unstable, shaky camera, "
        "repetitive motion, frozen frame, no motion"
    )
    
    return f"{base_negative}, {_get_negative_prompt(intent)}"

def _generate_video_diagnostics(settings: Dict[str, Any], intent: Dict[str, str]) -> Dict[str, str]:
    """
    Generate diagnostics specific to video generation.
    """
    return {
        "model_choice": f"{settings['model']} selected for video generation",
        "motion_setting": f"Motion bucket ID {settings['motion_bucket_id']} for {intent['style']} style",
        "frame_settings": f"{settings['num_frames']} frames at {settings['fps']} FPS",
        "cfg_reason": f"CFG {settings['cfg_scale']} optimized for video stability",
        "detected_style": intent["style"],
        "detected_mood": intent["mood"]
    }

# Shared helper functions
def _get_base_settings(goal: str, intent: Dict[str, str]) -> Dict[str, Any]:
    """Get base generation settings."""
    base = {
        "cfg_scale": 7.5,
        "steps": 28,
        "sampler": "DPM++ 2M Karras",
        "scheduler": "Karras",
        "denoise": 0.25
    }
    
    if goal == "t2i":
        base["resolution"] = "832x1216"
    elif goal == "i2i":
        base["resolution"] = "match_input"
    
    return base

def _get_negative_prompt(intent: Dict[str, str]) -> str:
    """Get style-aware negative prompt."""
    base = "blurry, low quality, watermark, artifacts, bad anatomy"
    return base

def _generate_diagnostics(settings: Dict[str, Any], intent: Dict[str, str], goal: str) -> Dict[str, str]:
    """Generate basic diagnostics."""
    return {
        "cfg_reason": f"CFG {settings['cfg_scale']} for {intent['style']} style",
        "goal": goal
    }
