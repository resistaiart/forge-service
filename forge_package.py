# forge_package.py
import time
import logging
from typing import Dict, List, Optional, Any
from functools import lru_cache

# Import the modules (consider using dependency injection for testability)
from forge_prompts import build_prompts
from forge_settings import build_settings
from forge_resources import validate_resources
from forge_captions import generate_captions
from forge_diagnostics import generate_diagnostics
from forge_benchmarking import run_benchmarks
from forge_profiles import load_profile, adapt_settings, adapt_captions
from forge_integrations import list_integrations

# Set up logging
logger = logging.getLogger(__name__)

# Removed the global PACKAGE_VERSION. Versioning is now based on timestamp and a request counter per session.
# For a unique ID, consider using a UUID instead.

def build_package(
    package_goal: str,
    prompt: str,
    resources: Optional[List[str]] = None,
    caption: Optional[str] = None,
    user_id: str = "default",
    descriptors: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Builds a full Forge Prompt Package by orchestrating various specialized modules.

    Args:
        package_goal: The intended use case for the package (e.g., 't2i', 't2v', 'i2i').
        prompt: The core input prompt from the user.
        resources: Optional list of external resources (LoRA, embeddings, etc.).
        caption: Optional description or caption for context.
        user_id: Identifier for loading user-specific profiles and settings.
        descriptors: Optional structured image descriptors from analysis.

    Returns:
        A comprehensive dictionary containing all optimized components needed for generation.

    Raises:
        ValueError: If the package_goal is invalid or essential components fail to build.
        RuntimeError: For unexpected errors during package construction.
    """
    # 1. Input Validation & Initialization
    logger.info(f"Building package for user '{user_id}' with goal '{package_goal}'")
    _validate_package_goal(package_goal)

    resources = resources or []
    profile = load_profile(user_id)
    start_time = time.time()

    # 2. Prompt Enrichment (More sophisticated logic)
    enriched_prompt = _enrich_prompt_with_descriptors(prompt, descriptors)

    package_components = {}
    try:
        # 3. Build Package Components
        # Consider making these steps more fault-tolerant. If a non-critical step fails, maybe log a warning and use a default?
        package_components['positive_prompt'], package_components['negative_prompt'] = build_prompts(enriched_prompt, profile)
        package_components['settings'] = build_settings(profile, package_goal)
        package_components['settings'] = adapt_settings(package_components['settings'], profile)
        package_components['resources'] = validate_resources(resources)
        package_components['captions'] = generate_captions(enriched_prompt, caption, profile)
        package_components['captions'] = adapt_captions(package_components['captions'], profile)
        package_components['diagnostics'] = generate_diagnostics(package_components['settings'], package_components['resources'])
        package_components['benchmarks'] = run_benchmarks()
        package_components['integrations'] = list_integrations(active_only=True) # Only show active integrations

    except Exception as e:
        logger.error(f"Failed to build a package component: {e}", exc_info=True)
        # Decide on error handling strategy:
        # 1. Re-raise the exception and let the API endpoint handle it (recommended)
        raise RuntimeError(f"Package construction failed during '{e.__class__.__name__}': {str(e)}")

    # 4. Assemble Final Package
    build_time = round(time.time() - start_time, 4)
    package_id = f"forge_pkg_{int(start_time)}"  # Simple unique ID based on timestamp

    package = {
        "id": package_id,
        "version": 1, # Keep version as 1 for now, or use a schema version
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"), # ISO 8601 format
        "build_time_seconds": build_time,
        "goal": package_goal,
        "positive_prompt": package_components['positive_prompt'],
        "negative_prompt": package_components['negative_prompt'],
        "settings": package_components['settings'],
        "resources": package_components['resources'],
        "captions": package_components['captions'],
        "diagnostics": {**package_components['diagnostics'], "build_time": build_time},
        "benchmarks": package_components['benchmarks'],
        "integrations": package_components['integrations'],
        "profile_used": profile
    }

    # Add optional metadata
    metadata = {}
    if caption:
        metadata["user_caption"] = caption
    if descriptors:
        metadata["image_descriptors"] = descriptors
    if metadata:
        package["metadata"] = metadata

    logger.info(f"Package {package_id} built successfully in {build_time}s for goal '{package_goal}'")
    return package

# --- Helper Functions ---

@lru_cache(maxsize=32)
def _validate_package_goal(goal: str):
    """Validates the provided package goal against a known set."""
    valid_goals = {"t2i", "t2v", "i2i", "i2v", "upscale", "interrogate"}
    if goal not in valid_goals:
        logger.warning(f"Invalid package goal requested: '{goal}'")
        raise ValueError(f"Unsupported package goal: '{goal}'. Must be one of: {sorted(valid_goals)}")

def _enrich_prompt_with_descriptors(base_prompt: str, descriptors: Optional[Dict[str, Any]]) -> str:
    """Intelligently merges image descriptors with the original prompt."""
    if not descriptors:
        return base_prompt

    # Extract descriptors
    subject = descriptors.get("subject", "").strip()
    style = descriptors.get("style", "").strip()
    tags = descriptors.get("tags", [])
    # Check if these elements are already strongly present in the base prompt to avoid duplication
    # This is a simple check; a more advanced NLP approach could be used here.
    prompt_lower = base_prompt.lower()
    new_elements = []

    if subject and subject.lower() not in prompt_lower:
        new_elements.append(subject)
    if style and style.lower() not in prompt_lower:
        new_elements.append(style)
    # For tags, add a couple of the most relevant ones not already present
    relevant_tags = [tag for tag in tags if tag.lower() not in prompt_lower][:3]
    if relevant_tags:
        new_elements.append(", ".join(relevant_tags))

    if new_elements:
        enriched_prompt = f"{base_prompt}, {', '.join(new_elements)}"
        logger.debug(f"Enriched prompt with descriptors: '{enriched_prompt}'")
        return enriched_prompt
    else:
        logger.debug("No new descriptors added to prompt")
        return base_prompt
