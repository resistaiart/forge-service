# forge_prompts.py

import random
import re

def clean_prompt(text: str) -> str:
    """
    Cleans up raw prompt text by removing unwanted characters
    and normalising whitespace.
    """
    text = re.sub(r'[^\w\s,.:;!?()\-\']', '', text)  # strip weird chars
    return " ".join(text.split())


def weight_keywords(prompt: str) -> str:
    """
    Adds basic emphasis weighting to strong words (art styles, moods, etc).
    """
    emphasis_words = [
        "cyberpunk", "samurai", "neon", "cinematic", "ultra-detailed",
        "portrait", "landscape", "anime", "fantasy", "realistic"
    ]
    for word in emphasis_words:
        pattern = re.compile(rf"\b{word}\b", re.IGNORECASE)
        prompt = pattern.sub(f"(({word}:1.3))", prompt)
    return prompt


def optimise_prompt_package(prompt: str, goal: str = "t2i") -> dict:
    """
    Main function: takes user input and builds an optimised
    prompt package for Forge.
    """

    # Step 1: Clean and weight
    base_prompt = clean_prompt(prompt)
    weighted_prompt = weight_keywords(base_prompt)

    # Step 2: Negative prompt (universal baseline)
    negative_prompt = (
        "blurry, low quality, watermark, artifacts, cropped, "
        "text, bad anatomy, extra limbs, fused fingers, distorted hands, deformed face"
    )

    # Step 3: Settings (basic defaults tuned for ComfyUI)
    settings = {
        "cfg_scale": 8.0,
        "steps": 30,
        "resolution": "768x1152" if goal == "t2i" else "768x768",
        "sampler": "DPM++ 2M Karras",
        "scheduler": "Karras",
        "denoise": 0.25,
        "seed": random.randint(1, 999999),
    }

    # Step 4: Build package
    package = {
        "goal": goal,
        "positive_prompt": weighted_prompt,
        "negative_prompt": negative_prompt,
        "settings": settings,
        "resources": [],
        "profile_used": {
            "verbosity": "normal",
            "caption_style": "balanced",
            "preferred_checkpoint": "forge-base-v1.safetensors",
        },
        "diagnostics": {
            "cfg_reason": "CFG 8.0 balances adherence and creativity.",
            "sampler_choice": "DPM++ 2M Karras chosen for stability in neon scenes.",
            "resolution_reason": "768x1152 optimised for cinematic aspect ratio.",
        },
    }

    return package
