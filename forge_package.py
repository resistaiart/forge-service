# forge_package.py
import time
import random
from forge_prompts import build_prompts
from forge_settings import build_settings
from forge_resources import validate_resources
from forge_captions import generate_captions
from forge_diagnostics import generate_diagnostics
from forge_benchmarking import run_benchmarks
from forge_profiles import update_profile, load_profile
from forge_integrations import list_integrations

# Simple versioning system (could be replaced with DB later)
PACKAGE_VERSION = 1

def build_package(package_goal, prompt, resources=None, caption=None, user_id="default"):
    global PACKAGE_VERSION

    # Ensure resources is a list
    resources = resources or []

    # Load user profile for adaptivity
    profile = load_profile(user_id)

    # Core sections
    positive_prompt, negative_prompt = build_prompts(prompt, profile)
    settings = build_settings(profile)
    resources_block = validate_resources(resources)
    captions = generate_captions(prompt, caption, profile)
    diagnostics = generate_diagnostics(settings, resources_block)
    benchmarks = run_benchmarks()
    integrations = list_integrations()

    # Versioning
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

    # Update profile (adaptivity)
    update_profile(user_id, profile)

    # Increment version for next run
    PACKAGE_VERSION += 1

    return package
