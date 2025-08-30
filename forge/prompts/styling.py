# forge/prompts/styling.py

import random
import logging
from typing import Dict, List, Optional

from forge.prompts.config import CONFIG

logger = logging.getLogger(__name__)


def analyze_prompt_style(prompt: str) -> Dict[str, float]:
    if not prompt:
        return {s: 0.0 for s in ["realistic", "anime", "cyberpunk", "fantasy", "painting", "scifi"]}
    
    prompt_lower = prompt.lower()
    style_scores = {k: 0 for k in ["realistic", "anime", "cyberpunk", "fantasy", "painting", "scifi"]}
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
    neg = CONFIG["negative_prompt"]
    if additional_negatives:
        neg += ", " + ", ".join([n for n in additional_negatives if n])
    return neg


def get_settings(goal: str = "t2i", style_analysis: Optional[Dict] = None) -> Dict:
    if goal not in CONFIG["settings"]:
        logger.warning(f"Unknown goal '{goal}', defaulting to 't2i'")
        goal = "t2i"

    settings = CONFIG["settings"][goal].copy()
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
