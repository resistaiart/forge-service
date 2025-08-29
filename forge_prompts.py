# forge_prompts.py
import re
import random
import logging
from typing import Dict, List, Optional, Tuple
from enum import Enum

# Import other modules
from forge_resources import validate_resources
from forge_checkpoints import suggest_checkpoints

# Set up logging
logger = logging.getLogger(__name__)

# Enums for better type safety
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

# =====================
# CONFIGURATION
# =====================
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
        "long neck, jpeg artifacts, compression artifacts, lowres, bad hands, "
        "error, extra digit, fewer digits, cropped, worst quality, low quality, "
        "normal quality, jpeg artifacts, signature, watermark, username, blurry"
    ),
    "settings": {
        "t2i": {
            "cfg_scale": 7.5,
            "steps": 28,
            "resolution": "832x1216",
            "sampler": SamplerType.DPM_PP_2M.value,
            "scheduler": "Karras",
            "denoise": 0.4,
            "batch_size": 1,
            "clip_skip": 2,
            "preferred_checkpoint": "forge-base-v1.safetensors",
        },
        "t2v": {
            "cfg_scale": 8.5,
            "steps": 35,
            "resolution": "768x768",
            "sampler": SamplerType.DPM_PP_2M.value,
            "scheduler": "Karras",
            "denoise": 0.25,
            "batch_size": 1,
            "fps": 24,
            "clip_skip": 2,
            "preferred_checkpoint": "forge-animate-v1.safetensors",
        },
        "i2i": {
            "cfg_scale": 7.0,
            "steps": 30,
            "resolution": "match_input",
            "sampler": SamplerType.DPM_PP_2M.value,
            "scheduler": "Karras",
            "denoise": 0.65,
            "batch_size": 1,
            "clip_skip": 2,
            "preferred_checkpoint": "forge-base-v1.safetensors",
        },
        "i2v": {
            "cfg_scale": 8.0,
            "steps": 40,
            "resolution": "768x768",
            "sampler": SamplerType.DPM_PP_2M.value,
            "scheduler": "Karras",
            "denoise": 0.35,
            "batch_size": 1,
            "fps": 20,
            "clip_skip": 2,
            "preferred_checkpoint": "forge-animate-v1.safetensors",
        },
        "upscale": {
            "cfg_scale": 6.0,
            "steps": 20,
            "resolution": "1024x1024",
            "sampler": SamplerType.EULER_A.value,
            "scheduler": "Simple",
            "denoise": 0.2,
            "batch_size": 1,
            "clip_skip": 1,
            "preferred_checkpoint": "forge-upscale-v1.safetensors",
        }
    }
}

# =====================
# UTILITY FUNCTIONS
# =====================
def clean_prompt(prompt: str) -> str:
    """Clean and normalize prompt text."""
    if not prompt or not isinstance(prompt, str):
        return ""
    
    # Remove extra whitespace and normalize punctuation
    prompt = re.sub(r"\s+", " ", prompt).strip()
    prompt = re.sub(r",\s*,", ",", prompt)
    prompt = re.sub(r"\.\s*\.", ".", prompt)
    
    # Remove duplicate words (simple deduplication)
    words = prompt.split()
    seen = set()
    unique_words = []
    for word in words:
        if word.lower() not in seen:
            seen.add(word.lower())
            unique_words.append(word)
    
    return " ".join(unique_words)

def weight_keywords(prompt: str, custom_weights: Optional[Dict] = None) -> str:
    """Apply emphasis weighting to important keywords."""
    if not prompt:
        return ""
    
    weights = {**_CONFIG["keyword_weights"], **(custom_weights or {})}
    
    # Sort by length (longest first) to avoid partial matches
    for word in sorted(weights.keys(), key=len, reverse=True):
        weight = weights[word]
        # Use word boundaries to avoid partial matches
        pattern = re.compile(rf"\b{re.escape(word)}\b", re.IGNORECASE)
        if pattern.search(prompt):
            prompt = pattern.sub(f"(({word}:{weight}))", prompt)
    
    return prompt

def analyze_prompt_style(prompt: str) -> Dict[str, float]:
    """Analyze prompt to detect artistic style preferences."""
    prompt_lower = prompt.lower()
    style_scores = {
        "realistic": 0, "anime": 0, "cyberpunk": 0, 
        "fantasy": 0, "painting": 0, "scifi": 0
    }
    
    style_keywords = {
        "realistic": ["realistic", "photorealistic", "photo", "hyperrealistic"],
        "anime": ["anime", "manga", "cel-shaded", "chibi", "kawaii"],
        "cyberpunk": ["cyberpunk", "neon", "futuristic", "dystopian"],
        "fantasy": ["fantasy", "magical", "dragon", "elf", "wizard"],
        "painting": ["oil painting", "watercolor", "acrylic", "impressionist"],
        "scifi": ["sci-fi", "spaceship", "alien", "robot", "future"]
    }
    
    for style, keywords in style_keywords.items():
        for keyword in keywords:
            if keyword in prompt_lower:
                style_scores[style] += 1
    
    # Normalize scores
    total = sum(style_scores.values())
    if total > 0:
        for style in style_scores:
            style_scores[style] = round(style_scores[style] / total, 2)
    
    return style_scores

def get_negative_prompt(additional_negatives: Optional[List[str]] = None) -> str:
    """Get negative prompt with optional additional terms."""
    negative = _CONFIG["negative_prompt"]
    if additional_negatives:
        negative += ", " + ", ".join([n for n in additional_negatives if n])
    return negative

def get_settings(goal: str = "t2i", style_analysis: Optional[Dict] = None) -> Dict:
    """Get settings for a goal with optional style-based adjustments."""
    if goal not in _CONFIG["settings"]:
        logger.warning(f"Unknown goal '{goal}', defaulting to 't2i'")
        goal = "t2i"
    
    settings = _CONFIG["settings"][goal].copy()
    settings["seed"] = random.randint(1, 999999999)
    
    # Apply style-based adjustments
    if style_analysis:
        dominant_style = max(style_analysis.items(), key=lambda x: x[1])[0]
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
    
    # Ensure reasonable bounds
    settings["cfg_scale"] = max(1.0, min(20.0, settings["cfg_scale"]))
    settings["steps"] = max(10, min(100, settings["steps"]))
    settings["denoise"] = max(0.0, min(1.0, settings["denoise"]))
    
    return settings

# =====================
# MAIN FUNCTIONS
# =====================
def build_prompts(prompt: str, profile: Optional[Dict] = None) -> Tuple[str, str]:
    """
    Build positive and negative prompts from input.
    Returns: (positive_prompt, negative_prompt)
    """
    cleaned_prompt = clean_prompt(prompt)
    weighted_prompt = weight_keywords(cleaned_prompt)
    negative_prompt = get_negative_prompt()
    
    return weighted_prompt, negative_prompt

def optimise_prompt_package(
    prompt: str,
    goal: str = "t2i",
    resources: Optional[List] = None,
    caption: Optional[str] = None,
    custom_weights: Optional[Dict] = None,
    checkpoint: Optional[str] = None
) -> Dict:
    """Build an optimized prompt package with comprehensive metadata."""
    
    try:
        # Validate input
        if not prompt or not isinstance(prompt, str):
            raise ValueError("Prompt must be a non-empty string")
        
        # Clean and analyze prompt
        base_prompt = clean_prompt(prompt)
        style_analysis = analyze_prompt_style(base_prompt)
        weighted_prompt = weight_keywords(base_prompt, custom_weights)
        
        # Get settings with style adjustments
        negative_prompt = get_negative_prompt()
        settings = get_settings(goal, style_analysis)
        
        # Validate resources
        validated_resources = validate_resources(resources or [])
        
        # Get checkpoint suggestions
        preferred_checkpoint = checkpoint or settings.get("preferred_checkpoint", "")
        checkpoint_suggestions = suggest_checkpoints(preferred_checkpoint)
        
        # Build diagnostics
        diagnostics = _build_diagnostics(settings, goal, style_analysis, validated_resources)
        
        # Assemble package
        package = {
            "goal": goal,
            "positive_prompt": weighted_prompt,
            "negative_prompt": negative_prompt,
            "settings": settings,
            "resources": validated_resources,
            "caption": caption or "",
            "style_analysis": style_analysis,
            "diagnostics": diagnostics,
            "metadata": {
                "prompt_length": len(weighted_prompt),
                "negative_length": len(negative_prompt),
                "resource_count": len(validated_resources),
                "word_count": len(weighted_prompt.split()),
            },
            "checkpoint_suggestions": checkpoint_suggestions,
        }
        
        logger.info(f"Built package for goal '{goal}' with {len(validated_resources)} resources")
        return package
        
    except Exception as e:
        logger.error(f"Failed to build prompt package: {e}")
        raise

def _build_diagnostics(settings: Dict, goal: str, style_analysis: Dict, resources: List) -> Dict:
    """Build detailed diagnostics explaining the choices."""
    diagnostics = {
        "cfg_reason": f"CFG {settings['cfg_scale']} tuned for {goal} balance",
        "sampler_choice": f"{settings['sampler']} chosen for stability and quality",
        "resolution_reason": f"{settings['resolution']} optimal for {goal} workflow",
        "denoise_reason": f"Denoise {settings['denoise']} preserves detail while allowing creativity",
        "steps_reason": f"{settings['steps']} steps for quality-speed balance",
    }
    
    # Add style-specific reasoning
    dominant_style = max(style_analysis.items(), key=lambda x: x[1])
    if dominant_style[1] > 0.3:  # Only mention if significant
        diagnostics["style_influence"] = f"Detected {dominant_style[0]} style influencing parameters"
    
    # Add resource information
    if resources:
        diagnostics["resources_used"] = f"Using {len(resources)} validated resources"
    
    # Goal-specific diagnostics
    if goal == "t2v":
        diagnostics["fps_reason"] = f"{settings.get('fps', 24)}fps for natural motion"
    elif goal == "i2i":
        diagnostics["transform_strength"] = f"Denoise {settings['denoise']} controls transformation intensity"
    
    return diagnostics

# =====================
# EXAMPLE USAGE
# =====================
if __name__ == "__main__":
    # Test the function
    test_package = optimise_prompt_package(
        prompt="a cyberpunk samurai under neon rain, masterpiece, best quality, 4k",
        goal="t2i",
        resources=[{"name": "Cyberpunk Style", "type": "lora"}],
        custom_weights={"cyberpunk": 1.4, "neon": 1.3}
    )
    
    from pprint import pprint
    print("=== Optimized Prompt Package ===")
    pprint(test_package)
    
    # Test style analysis
    print("\n=== Style Analysis ===")
    analysis = analyze_prompt_style("cyberpunk samurai with neon lights and futuristic city")
    pprint(analysis)
