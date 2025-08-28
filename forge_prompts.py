# forge_prompts.py
import re
import random
from typing import Dict, List, Optional
from forge_resources import validate_resources

# --- CONFIGURATION (Forge-minimalist, ComfyUI-ready) ---
_CONFIG = {
    "keyword_weights": {
        "cyberpunk": 1.3,
        "samurai": 1.3,
        "neon": 1.2,
        "cinematic": 1.4,
        "ultra-detailed": 1.5,
        "portrait": 1.3,
        "landscape": 1.3,
        "masterpiece": 1.6,
        "best quality": 1.5,
    },
    "negative_prompt": (
        "blurry, low quality, watermark, text, signature, username, artist name, "
        "bad anatomy, extra limbs, fused fingers, distorted hands, deformed face, "
        "poorly drawn hands, mutation, ugly, disfigured, bad proportions, "
        "cropped, cloned face, malformed limbs, missing arms, missing legs, "
        "too many fingers, long neck, jpeg artifacts, compression artifacts"
    ),
    "settings": {
        "t2i": {
            "cfg_scale": 7.5,
            "steps": 28,
            "resolution": "832x1216",
            "sampler": "DPM++ 2M Karras",
            "scheduler": "Karras",
            "denoise": 0.0,
            "batch_size": 1,
            "clip_skip": 2,
            "fps": None,
            "vae": "vae-ft-mse-840000-ema-pruned.safetensors",
            "lora": [],
            "vae_tiling": False,
            "hires_fix": True,
            "preferred_checkpoint": "forge-base-v1.safetensors",
        },
        "t2v": {
            "cfg_scale": 8.5,
            "steps": 35,
            "resolution": "768x768",
            "sampler": "DPM++ 2M Karras",
            "scheduler": "Karras",
            "denoise": 0.25,
            "batch_size": 8,
            "clip_skip": 2,
            "fps": 24,
            "vae": "vae-ft-mse-840000-ema-pruned.safetensors",
            "lora": [],
            "vae_tiling": False,
            "hires_fix": False,
            "preferred_checkpoint": "forge-animate-v1.safetensors",
        },
        "upscale": {
            "cfg_scale": 6.0,
            "steps": 20,
            "resolution": "1024x1024",
            "sampler": "Euler a",
            "scheduler": "Simple",
            "denoise": 0.4,
            "batch_size": 1,
            "clip_skip": 2,
            "fps": None,
            "vae": "vae-ft-mse-840000-ema-pruned.safetensors",
            "lora": [],
            "vae_tiling": True,
            "hires_fix": False,
            "preferred_checkpoint": "forge-upscale-v1.safetensors",
        }
    }
}

# --- CORE UTILITIES ---

def clean_prompt(prompt: str) -> str:
    """Remove redundant spaces, normalize punctuation, clean prompt."""
    prompt = re.sub(r"\s+", " ", prompt).strip()
    prompt = re.sub(r",\s*,", ",", prompt)
    prompt = re.sub(r"\.\s*\.", ".", prompt)
    return prompt

def weight_keywords(prompt: str, custom_weights: Optional[Dict] = None) -> str:
    """Apply emphasis to key terms with configurable weighting."""
    weights = custom_weights or _CONFIG["keyword_weights"]
    for word in sorted(weights.keys(), key=len, reverse=True):
        weight = weights[word]
        pattern = re.compile(rf"\b{re.escape(word)}\b", re.IGNORECASE)
        if pattern.search(prompt):
            prompt = pattern.sub(f"(({word}:{weight}))", prompt)
    return prompt

def get_negative_prompt(additional_negatives: Optional[List[str]] = None) -> str:
    """Return standard Forge negative prompt string."""
    negative = _CONFIG["negative_prompt"]
    if additional_negatives:
        negative += ", " + ", ".join(additional_negatives)
    return negative

def get_settings(goal: str = "t2i") -> Dict:
    """Return full ComfyUI-ready settings for given goal."""
    settings = _CONFIG["settings"].get(goal, _CONFIG["settings"]["t2i"]).copy()
    settings["seed"] = random.randint(1, 999999999)
    return settings

# --- MAIN BUILDER ---

def optimise_prompt_package(
    prompt: str,
    goal: str = "t2i",
    resources: Optional[List] = None,
    caption: Optional[str] = None,
    custom_weights: Optional[Dict] = None
) -> Dict:
    """Build a Forge-ready, ComfyUI-compatible prompt package."""
    base_prompt = clean_prompt(prompt)
    weighted_prompt = weight_keywords(base_prompt, custom_weights)
    negative_prompt = get_negative_prompt()
    settings = get_settings(goal)
    validated_resources = validate_resources(resources or [])

    diagnostics = {
        "cfg_reason": f"CFG {settings['cfg_scale']} tuned for {goal}",
        "sampler_choice": f"{settings['sampler']} chosen for stability/quality",
        "resolution_reason": f"{settings['resolution']} optimal for {goal}",
        "resource_count": len(validated_resources),
        "active_resources": [r["name"] for r in validated_resources if r["health"] == "active"],
    }

    package = {
        "goal": goal,
        "positive_prompt": weighted_prompt,
        "negative_prompt": negative_prompt,
        "settings": settings,
        "resources": validated_resources,
        "caption": caption or "",
        "profile_used": {
            "verbosity": "normal",
            "caption_style": "balanced",
            "preferred_checkpoint": settings.get("preferred_checkpoint"),
        },
        "diagnostics": diagnostics,
        "metadata": {
            "prompt_length": len(weighted_prompt),
            "negative_length": len(negative_prompt),
            "resource_count": len(validated_resources),
        }
    }
    return package

# --- EXAMPLE RUN ---
if __name__ == "__main__":
    test = optimise_prompt_package(
        prompt="a cyberpunk samurai under neon rain, masterpiece, best quality",
        goal="t2i",
        resources=[
            {"name": "Old Cyberpunk Model", "type": "model", "creator": "AI Artist"},
            {"name": "NSFW dataset", "type": "dataset", "health": "inactive"},
        ],
    )
    from pprint import pprint
    print("=== Forge Prompt Package (t2i) ===")
    pprint(test)
