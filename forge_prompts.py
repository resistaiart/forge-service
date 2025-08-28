# forge_prompts.py
import re
import random

def clean_prompt(prompt: str) -> str:
    """Clean whitespace and normalize input prompt"""
    return re.sub(r"\s+", " ", prompt.strip())

def weight_keywords(prompt: str) -> str:
    """Apply weighting to important words"""
    weights = {"cyberpunk": 1.3, "samurai": 1.3, "neon": 1.2, "cinematic": 1.4}
    for word, weight in weights.items():
        prompt = re.sub(rf"\b{word}\b", f"(({word}:{weight}))", prompt, flags=re.IGNORECASE)
    return prompt

def optimise_prompt_package(
    prompt: str,
    goal: str = "t2i",
    resources: list = None,
    caption: str = None
) -> dict:
    """
    Build an optimised prompt package for text-to-image or text-to-video
    Returns Forge-standard envelope: {outcome, result, message}
    """
    try:
        base_prompt = clean_prompt(prompt)
        weighted_prompt = weight_keywords(base_prompt)

        # Simplified settings
        settings = {
            "cfg_scale": 8.0,
            "steps": 30,
            "resolution": "768x1152" if goal == "t2i" else "768x768",
            "sampler": "DPM++ 2M Karras",
            "scheduler": "Karras",
            "seed": random.randint(1, 999999999),
        }

        diagnostics = {
            "cfg_reason": f"CFG {settings['cfg_scale']} balances adherence & creativity",
            "resolution_reason": f"{settings['resolution']} optimised for {goal}",
            "sampler_choice": "DPM++ 2M Karras chosen for stability",
        }

        package = {
            "goal": goal,
            "positive_prompt": weighted_prompt,
            "negative_prompt": (
                "blurry, low quality, watermark, artifacts, text, bad anatomy, extra limbs"
            ),
            "settings": settings,
            "resources": resources or [],
            "caption": caption,
            "diagnostics": diagnostics,
        }

        return {"outcome": "success", "result": package, "message": "optimised"}
    except Exception as e:
        return {"outcome": "error", "message": f"optimise failed: {str(e)}", "result": None}
