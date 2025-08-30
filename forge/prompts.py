# forge/prompts.py
import re
import random
import logging
from typing import Dict, List, Optional, Tuple
from enum import Enum

from forge.resources import validate_resources
from forge.checkpoints import suggest_checkpoints

logger = logging.getLogger(__name__)


class GenerationGoal(Enum):
    T2I = "t2i"
    T2V = "t2v"
    I2I = "i2i"
    I2V = "i2v"
    UPSCALE = "upscale"
    INTERROGATE = "interrogate"


class SamplerType(Enum):
    DPM_PP_2M = "DPM++ 2M Karras"
    EULER_A = "Euler a"
    EULER = "Euler"
    LMS = "LMS"
    DDIM = "DDIM"


_CONFIG = {
    "keyword_weights": {
        "cyberpunk": 1.3, "samurai": 1.3, "neon": 1.2, "cinematic": 1.4,
        "ultra-detailed": 1.5, "portrait": 1.3, "landscape": 1.3,
        "masterpiece": 1.6, "best quality": 1.5, "4k": 1.4, "8k": 1.4,
        "photorealistic": 1.4, "hyperrealistic": 1.5, "anime": 1.3,
        "fantasy": 1.3, "scifi": 1.3, "concept art": 1.4
    },
    "negative_prompt": (
        "blurry, low quality, watermark, text, signature, username, artist name, "
        "bad anatomy, extra limbs, fused fingers, distorted hands, deformed face, "
        "poorly drawn hands, poorly drawn face, mutation, mutated, ugly, disfigured, "
        "bad proportions, cloned face, malformed limbs, missing arms, missing legs, "
        "extra arms, extra legs, mutated hands, fused fingers, too many fingers, "
        "long neck, jpeg artifacts, compression artifacts, lowres, error, "
        "extra digit, fewer digits, cropped, worst quality, normal quality"
    ),
    "settings": {
        "t2i": {
            "cfg_scale": 7.5, "steps": 28, "resolution": "832x1216",
            "sampler": SamplerType.DPM_PP_2M.value, "scheduler": "Karras",
            "denoise": 0.4, "batch_size": 1, "clip_skip": 2,
            "preferred_checkpoint": "forge-base-v1.safetensors",
        },
        "t2v": {
            "cfg_scale": 8.5, "steps": 35, "resolution": "768x768",
            "sampler": SamplerType.DPM_PP_2M.value, "scheduler": "Karras",
            "denoise": 0.25, "batch_size": 1, "fps": 24, "clip_skip": 2,
            "preferred_checkpoint": "forge-animate-v1.safetensors",
        },
        "i2i": {
            "cfg_scale": 7.0, "steps": 30, "resolution": "match_input",
            "sampler": SamplerType.DPM_PP_2M.value, "scheduler": "Karras",
            "denoise": 0.65, "batch_size": 1, "clip_skip": 2,
            "preferred_checkpoint": "forge-base-v1.safetensors",
        },
        "i2v": {
            "cfg_scale": 8.0, "steps": 40, "resolution": "768x768",
            "sampler": SamplerType.DPM_PP_2M.value, "scheduler": "Karras",
            "denoise": 0.35, "batch_size": 1, "fps": 20, "clip_skip": 2,
            "preferred_checkpoint": "forge-animate-v1.safetensors",
        },
        "upscale": {
            "cfg_scale": 6.0, "steps": 20, "resolution": "1024x1024",
            "sampler": SamplerType.EULER_A.value, "scheduler": "Simple",
            "denoise": 0.2, "batch_size": 1, "clip_skip": 1,
            "preferred_checkpoint": "forge-upscale-v1.safetensors",
        }
    }
}


def clean_prompt(prompt: str) -> str:
    if not prompt or not isinstance(prompt, str):
        return ""
    prompt = re.sub(r"\s+", " ", prompt).strip()
    prompt = re.sub(r",\s*,", ",", prompt)
    prompt = re.sub(r"\.\s*\.", ".", prompt)
    seen, unique_words = set(), []
    for word in prompt.split():
        if word.lower() not in seen:
            seen.add(word.lower())
            unique_words.append(word)
    return " ".join(unique_words)


def weight_keywords(prompt: str, custom_weights: Optional[Dict] = None) -> str:
    if not prompt:
        return ""
    weights = {**_CONFIG["keyword_weights"], **(custom_weights or {})}
    for word in sorted(weights.keys(), key=len, reverse=True):
        pattern = re.compile(rf"\b{re.escape(word)}\b", re.IGNORECASE)
        if pattern.search(prompt):
            prompt = pattern.sub(f"(({word}:{weights[word]}))", prompt)
    return prompt


def analyze_prompt_style(prompt: str) -> Dict[str, float]:
    if not prompt:
        return {s: 0.0 for s in ["realistic","anime","cyberpunk","fantasy","painting","scifi"]}
    prompt_lower = prompt.lower()
    style_scores = {k: 0 for k in ["realistic","anime","cyberpunk","fantasy","painting","scifi"]}
    style_keywords = {
        "realistic": ["realistic", "photorealistic", "photo", "hyperrealistic"],
        "anime": ["anime", "manga", "cel-shaded", "chibi", "kawaii"],
        "cyberpunk": ["cyberpunk", "neon", "futuristic", "dystopian"],
        "fantasy": ["fantasy", "magical", "dragon", "elf", "wizard"],
        "painting": ["oil painting", "watercolor", "acrylic", "impressionist"],
        "scifi": ["sci-fi", "spaceship", "alien", "robot", "future"],
    }
    for style, keywords in style_keywords.items():
        for keyword in keywords:
            if keyword in prompt_lower:
                style_scores[style] += 1
    total = sum(style_scores.values())
    if total:
        for style in style_scores:
            style_scores[style] = round(style_scores[style] / total, 2)
    return style_scores


def get_negative_prompt(additional_negatives: Optional[List[str]] = None) -> str:
    neg = _CONFIG["negative_prompt"]
    if additional_negatives:
        neg += ", " + ", ".join([n for n in additional_negatives if n])
    return neg


def get_settings(goal: str = "t2i", style_analysis: Optional[Dict] = None) -> Dict:
    if goal not in _CONFIG["settings"]:
        logger.warning(f"Unknown goal '{goal}', defaulting to 't2i'")
        goal = "t2i"
    settings = _CONFIG["settings"][goal].copy()
    settings["seed"] = random.randint(1, 999999999)
    if style_analysis:
        dominant_style, score = max(style_analysis.items(), key=lambda x: x[1])
        if score > 0:
            style_adjustments = {
                "realistic": {"cfg_scale": -0.5, "steps": 5},
                "anime": {"cfg_scale": 0.3, "steps": -2},
                "cyberpunk": {"cfg_scale": 0.7, "steps": 3},
                "fantasy": {"cfg_scale": 0.4, "steps": 2},
            }
            if dominant_style in style_adjustments:
                adj = style_adjustments[dominant_style]
                settings["cfg_scale"] += adj.get("cfg_scale", 0)
                settings["steps"] += adj.get("steps", 0)
    settings["cfg_scale"] = max(1.0, min(20.0, settings["cfg_scale"]))
    settings["steps"] = max(10, min(100, settings["steps"]))
    settings["denoise"] = max(0.0, min(1.0, settings["denoise"]))
    return settings


def build_prompts(prompt: str, profile: Optional[Dict] = None) -> Tuple[str, str]:
    if not prompt or not isinstance(prompt, str):
        return "", get_negative_prompt()
    cleaned = clean_prompt(prompt)
    weighted = weight_keywords(cleaned, profile.get("custom_weights") if profile else None)
    return weighted or cleaned, get_negative_prompt()


def optimise_prompt_package(
    prompt: str,
    goal: str = "t2i",
    resources: Optional[List] = None,
    caption: Optional[str] = None,
    custom_weights: Optional[Dict] = None,
    checkpoint: Optional[str] = None
) -> Dict:
    try:
        if not prompt or not isinstance(prompt, str):
            raise ValueError("Prompt must be a non-empty string")
        base_prompt = clean_prompt(prompt)
        style_analysis = analyze_prompt_style(base_prompt)
        weighted_prompt = weight_keywords(base_prompt, custom_weights)
        negative_prompt = get_negative_prompt()
        settings = get_settings(goal, style_analysis)
        validated_resources = validate_resources(resources or [])
        checkpoint_suggestions = suggest_checkpoints(checkpoint or settings.get("preferred_checkpoint", ""))
        diagnostics = _build_diagnostics(settings, goal, style_analysis, validated_resources)
        return {
            "goal": goal,
            "positive_prompt": weighted_prompt or base_prompt,
            "negative_prompt": negative_prompt,
            "settings": settings,
            "resources": validated_resources,
            "caption": caption or "",
            "style_analysis": style_analysis,
            "diagnostics": diagnostics,
            "metadata": {
                "prompt_length": len(weighted_prompt or base_prompt),
                "negative_length": len(negative_prompt),
                "resource_count": len(validated_resources),
                "word_count": len((weighted_prompt or base_prompt).split()),
            },
            "checkpoint_suggestions": checkpoint_suggestions,
        }
    except Exception as e:
        logger.error(f"Failed to build prompt package: {e}", exc_info=True)
        raise


def _build_diagnostics(settings: Dict, goal: str, style_analysis: Dict, resources: List) -> Dict:
    diag = {
        "cfg_reason": f"CFG {settings['cfg_scale']} tuned for {goal} balance",
        "sampler_choice": f"{settings['sampler']} chosen for stability and quality",
        "resolution_reason": f"{settings['resolution']} optimal for {goal} workflow",
        "denoise_reason": f"Denoise {settings['denoise']} preserves detail while allowing creativity",
        "steps_reason": f"{settings['steps']} steps for quality-speed balance",
    }
    if style_analysis:
        dominant_style, score = max(style_analysis.items(), key=lambda x: x[1])
        if score > 0.3:
            diag["style_influence"] = f"Detected {dominant_style} style influencing parameters"
    if resources:
        diag["resources_used"] = f"Using {len(resources)} validated resources"
    if goal == "t2v":
        diag["fps_reason"] = f"{settings.get('fps', 24)}fps for natural motion"
    elif goal == "i2i":
        diag["transform_strength"] = f"Denoise {settings['denoise']} controls transformation intensity"
    return diag
