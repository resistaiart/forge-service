# forge/prompts/builder.py

import logging
from typing import List, Dict, Optional, Tuple

from forge.prompts.cleaning import clean_prompt, weight_keywords
from forge.prompts.styling import analyze_prompt_style, get_negative_prompt, get_settings
from forge.resources import validate_resources
from forge.checkpoints import suggest_checkpoints

logger = logging.getLogger(__name__)


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
        dominant_st_
