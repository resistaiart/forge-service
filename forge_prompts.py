# forge_prompts.py
import re
import random

def clean_prompt(prompt: str) -> str:
    return prompt.strip().replace("\n", " ")

def weight_keywords(prompt: str) -> str:
    important_words = ["cyberpunk", "samurai", "neon", "cinematic"]
    for word in important_words:
        pattern = re.compile(rf"\b{word}\b", re.IGNORECASE)
        prompt = pattern.sub(f"(({word}:1.3))", prompt)
    return prompt

def get_negative_prompt() -> str:
    return (
        "blurry, low quality, watermark, artifacts, cropped, "
        "text, bad anatomy, extra limbs, fused fingers, distorted hands, deformed face"
    )

def optimise_prompt_package(
    prompt: str, goal: str = "t2i", resources: list = None, caption: str = None
) -> dict:
    """
    Forge-standard optimised package for text-to-image (t2i) or text-to-video (t2v).
    Always wrapped in {outcome, result, message}.
    """
    try:
        cleaned = clean_prompt(prompt)
        weighted = weight_keywords(cleaned)
        negative_prompt = get_negative_prompt()

        settings = {
            "cfg_scale": 8.0,
            "steps": 30,
            "resolution": "768x1152" if goal == "t2i" else "768x768",
            "sampler": "DPM++ 2M Karras",
            "scheduler": "Karras",
            "seed": random.randint(1, 999999),
        }

        diagnostics = {
            "cfg_reason": f"CFG {settings['cfg_scale']} balances adherence + creativity",
            "resolution_reason": f"{settings['resolution']} tuned for {goal}",
            "sampler_choice": "DPM++ 2M Karras for stability",
        }

        package = {
            "goal": goal,
            "positive_prompt": weighted,
            "negative_prompt": negative_prompt,
            "settings": settings,
            "resources": resources or [],
            "caption": caption,
            "profile_used": {
                "verbosity": "normal",
                "caption_style": "balanced",
                "preferred_checkpoint": "forge-base-v1.safetensors",
            },
            "diagnostics": diagnostics,
        }

        return {
            "outcome": "success",
            "result": package,
            "message": f"optimised for {goal}",
        }

    except Exception as e:
        return {
            "outcome": "error",
            "result": None,
            "message": f"optimisation failed {str(e)}",
        }
