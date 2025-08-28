# forge_package.py
import time
from forge_prompts import build_prompts
from forge_settings import build_settings
from forge_resources import validate_resources
from forge_captions import generate_captions
from forge_diagnostics import generate_diagnostics
from forge_benchmarking import run_benchmarks
from forge_profiles import update_profile, load_profile, adapt_settings, adapt_captions
from forge_integrations import list_integrations

PACKAGE_VERSION = 1

def build_package(package_goal, prompt, resources=None, caption=None, user_id="default", descriptors=None):
    """
    Build a full Prompt Package.
    If image descriptors are provided, they will enrich the prompt and be included.
    """
    global PACKAGE_VERSION

    resources = resources or []
    profile = load_profile(user_id)

    # If image descriptors exist, enrich the prompt
    enriched_prompt = prompt
    if descriptors:
        desc_subject = descriptors.get("subject", "")
        desc_style = descriptors.get("style", "")
        desc_tags = ", ".join(descriptors.get("tags", []))
        enriched_prompt = f"{prompt}, {desc_subject}, {desc_style}, {desc_tags}"

    # Build package components
    positive_prompt, negative_prompt = build_prompts(enriched_prompt, profile)
    settings = build_settings(profile, package_goal)
    settings = adapt_settings(settings, profile)
    resources_block = validate_resources(resources)
    captions = generate_captions(enriched_prompt, caption, profile)
    captions = adapt_captions(captions, profile)
    diagnostics = generate_diagnostics(settings, resources_block)
    benchmarks = run_benchmarks()
    integrations = list_integrations()

    package = {
        "version": PACKAGE_VERSION,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "goal": package_goal,
        "positive_prompt": positive_prompt,
        "negative_prompt": negative_prompt,
        "settings": settings,
        "resources": resources_block,
        "captions": captions,
        "diagnostics": diagnostics,
        "benchmarks": benchmarks,
        "integrations": integrations,
        "profile_used": profile
    }

    if caption:
        package["metadata"] = {"caption": caption}
    if descriptors:
        package["image_descriptors"] = descriptors

    update_profile(user_id, profile)
    PACKAGE_VERSION += 1

    return package
