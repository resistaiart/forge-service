# forge/package.py
import time
import logging
from typing import Dict, List, Optional, Any
from functools import lru_cache

# Imports from the forge modules
from forge.prompts import build_prompts
from forge.settings import build_settings
from forge.resources import validate_resources
from forge.captions import generate_captions
from forge.diagnostics import generate_diagnostics
from forge.benchmarking import run_benchmarks
from forge.profiles import load_profile, adapt_settings, adapt_captions
from forge.integrations import list_integrations
from forge.comfy_patches import generate_workflow_patch
from forge.safety import safety_scrub, build_safety

logger = logging.getLogger(__name__)


def build_package(
    package_goal: str,
    prompt: str,
    resources: Optional[List[str]] = None,
    caption: Optional[str] = None,
    user_id: str = "default",
    descriptors: Optional[Dict[str, Any]] = None,
    allow_nsfw: bool = False,
) -> Dict[str, Any]:
    """
    Build a full Forge Prompt Package by orchestrating specialized modules.
    Returns a dictionary aligned with ForgePromptPackage contract.
    """

    logger.info(f"Building package for user '{user_id}' with goal '{package_goal}'")
    _validate_package_goal(package_goal)

    # Scrub prompt for safety
    cleaned_prompt = safety_scrub(prompt, allow_nsfw=allow_nsfw)

    resources = resources or []
    profile = load_profile(user_id)
    start_time = time.time()

    # Enrich prompt with descriptors
    enriched_prompt = _enrich_prompt_with_descriptors(cleaned_prompt, descriptors)

    try:
        # Build components
        pos_prompt, neg_prompt = build_prompts(enriched_prompt, profile)
        settings = build_settings(profile, package_goal)
        settings = adapt_settings(settings, profile)
        validated_resources = validate_resources(resources)
        captions = generate_captions(enriched_prompt, caption, profile)
        captions = adapt_captions(captions, profile)
        diagnostics = generate_diagnostics(settings, validated_resources)
        benchmarks = run_benchmarks()
        integrations = list_integrations(active_only=True)

    except Exception as e:
        logger.error(f"Failed to build a package component: {e}", exc_info=True)
        raise RuntimeError(
            f"Package construction failed during '{e.__class__.__name__}': {str(e)}"
        )

    # Final assembly
    build_time = round(time.time() - start_time, 4)
    package_id = f"forge_pkg_{int(start_time)}"

    package = {
        "package_version": "v1.0",
        "positive": pos_prompt,
        "negative": neg_prompt,
        "config": settings,
        "workflow_patch": generate_workflow_patch(settings),
        "safety": build_safety(validated_resources, nsfw_allowed=allow_nsfw),
        "menus": ["variants", "prompt", "config", "workflow", "help"],
        "package_goal": package_goal,
        # --- audit / extras ---
        "id": package_id,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "build_time_seconds": build_time,
        "diagnostics": {**diagnostics, "build_time": build_time},
        "benchmarks": benchmarks,
        "integrations": integrations,
        "profile_used": profile,
    }

    metadata = {}
    if caption:
        metadata["user_caption"] = caption
    if descriptors:
        metadata["image_descriptors"] = descriptors
    if metadata:
        package["metadata"] = metadata

    logger.info(
        f"Package {package_id} built successfully in {build_time}s for goal '{package_goal}'"
    )
    return package


# --- Helpers ---

@lru_cache(maxsize=32)
def _validate_package_goal(goal: str):
    valid_goals = {"t2i", "t2v", "i2i", "i2v", "upscale", "interrogate"}
    if goal not in valid_goals:
        logger.warning(f"Invalid package goal requested: '{goal}'")
        raise ValueError(
            f"Unsupported package goal: '{goal}'. Must be one of: {sorted(valid_goals)}"
        )


def _enrich_prompt_with_descriptors(
    base_prompt: str, descriptors: Optional[Dict[str, Any]]
) -> str:
    if not descriptors:
        return base_prompt

    subject = descriptors.get("subject", "").strip()
    style = descriptors.get("style", "").strip()
    tags = descriptors.get("tags", [])
    prompt_lower = base_prompt.lower()
    new_elements = []

    if subject and subject.lower() not in prompt_lower:
        new_elements.append(subject)
    if style and style.lower() not in prompt_lower:
        new_elements.append(style)

    relevant_tags = [tag for tag in tags if tag.lower() not in prompt_lower][:3]
    if relevant_tags:
        new_elements.append(", ".join(relevant_tags))

    if new_elements:
        return f"{base_prompt}, {', '.join(new_elements)}"
    return base_prompt
