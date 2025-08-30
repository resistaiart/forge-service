import random
import logging
from typing import Dict, List, Optional

from forge.prompts.config import CONFIG

logger = logging.getLogger(__name__)


def analyze_prompt_style(prompt: str) -> Dict[str, float]:
    """
    Analyze prompt to determine stylistic influences based on known keywords.
    Returns a score distribution across known styles.
    """
    styles = ["realistic", "anime", "cyberpunk", "fantasy", "painting", "scifi"]
    if not prompt:
        return {style: 0.0 for style in styles}

    style_scores = dict.fromkeys(styles, 0)
    prompt_lower = prompt.lower()

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
    if total > 0:
        for style in style_scores:
            style_scores[style] = round(style_scores[style] / total, 2)

    return style_scores


def get_negative_prompt(additional_negatives: Optional[List[str]] = None) -> str:
    """
    Combine default negatives with any additional user-specified negatives.
    """
    base = CONFIG["negative_prompt"]
    if additional_negatives:
        extras = ", ".join(n for n in additional_negatives if n)
        return f"{base}, {extras}"
    return base


def get_settings(goal: str = "t2i", style_analysis: Optional[Dict[str, float]] = None) -> Dict:
    """
    Retrieve base generation settings, optionally modified by detected style.
    """
    if goal not in CONFIG["settings"]:
        logger.warning(f"Unknown generation goal '{goal}', defaulting to 't2i'")
        goal = "t2i"

    settings = CONFIG["settings"][goal].copy()
    settings["seed"] = random.randint(1, 999_999_999)

    if style_analysis:
        dominant_style, score = max(style_analysis.items(), key=lambda item: item[1])
        if score > 0:
            modifiers = {
                "realistic": {"cfg_scale": -0.5, "steps": 5},
                "anime": {"cfg_scale": 0.3, "steps": -2},
                "cyberpunk": {"cfg_scale": 0.7, "steps": 3},
                "fantasy": {"cfg_scale": 0.4, "steps": 2},
            }
            if dominant_style in modifiers:
                adj = modifiers[dominant_style]
                settings["cfg_scale"] += adj.get("cfg_scale", 0)
                settings["steps"] += adj.get("steps", 0)

    # Clamp values to safe bounds
    settings["cfg_scale"] = max(1.0, min(20.0, settings["cfg_scale"]))
    settings["steps"] = max(10, min(100, settings["steps"]))
    settings["denoise"] = max(0.0, min(1.0, settings["denoise"]))

    return settings
