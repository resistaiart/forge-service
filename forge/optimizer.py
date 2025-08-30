# forge/optimizer.py — Sealed Package Orchestrator 🔒

import logging
from typing import Dict, Any

from forge.safety import safety_scrub
from forge.prompts import build_prompts, analyze_prompt_style
from forge.settings import build_settings
from forge.resources import validate_resources
from forge.captions import generate_captions
from forge.comfy_patches import generate_workflow_patch
from forge.profiles import load_profile, adapt_settings, adapt_captions

logger = logging.getLogger(__name__)


def optimise_sealed(request: Dict[str, Any]) -> Dict[str, Any]:
    """🔒 SEALED: Orchestrates Forge modules to produce a sealed prompt package."""

    try:
        # 1. Safety filtering
        allow_nsfw = False
        if isinstance(request.get("profile"), dict):
            allow_nsfw = request["profile"].get("content_preferences", {}).get("allow_nsfw", False)

        cleaned_prompt = safety_scrub(request.get("prompt", ""), allow_nsfw=allow_nsfw)
        logger.debug(f"Prompt scrubbed → {cleaned_prompt[:80]}...")

        # 2. Intent analysis
        intent = analyze_prompt_style(cleaned_prompt)
        logger.debug(f"Prompt intent → {intent}")

        # 3. Prompt generation
        positive, negative = build_prompts(cleaned_prompt, intent)

        # 4. Config generation
        base_settings = build_settings(request["package_goal"], intent)

        # 5. Resource filtering
        resources = validate_resources(request.get("resources", []))

        # 6. Captions
        captions = generate_captions(cleaned_prompt, request.get("caption"))

        # 7. Workflow patch
        workflow_patch = generate_workflow_patch(base_settings)

        # 8. Final package
        return {
            "package_version": "v1.0",
            "positive": positive,
            "negative": negative,
            "config": base_settings,
            "workflow_patch": workflow_patch,
            "safety": {
                "status": "cleaned",
                "nsfw_allowed": allow_nsfw,
                "resources": resources,
            },
            "menus": _get_menus(request["package_goal"]),
            "package_goal": request["package_goal"],
            "captions": captions,
        }

    except Exception as e:
        logger.exception(f"Forge optimisation failed: {e}")
        return {
            "package_version": "v1.0",
            "outcome": "error",
            "message": f"Forge optimisation failed: {str(e)}"
        }


def _get_menus(package_goal: str) -> list:
    """Get appropriate menus for the package goal."""
    base_menus = [
        "variants", "prompt", "negatives", "config", "workflow",
        "safety", "version", "rationale", "discard", "help",
    ]

    if package_goal in ["i2i", "i2v"]:
        base_menus.append("denoise")
    if package_goal in ["t2v", "i2v"]:
        base_menus.extend(["frames", "motion"])

    return base_menus
