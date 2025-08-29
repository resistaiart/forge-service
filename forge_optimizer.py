# forge_optimizer.py
# 🔒 PRIVATE IMPLEMENTATION - Orchestrates your existing modules

from forge_safety import safety_scrub
from forge_prompts import build_prompts, analyze_prompt_style
from forge_settings import build_settings
from forge_resources import validate_resources
from forge_captions import generate_captions
from forge_comfy_patches import generate_workflow_patch  # ✅ CORRECTED - uses new file
from forge_profiles import load_profile, adapt_settings, adapt_captions

def optimize_sealed(request: dict) -> dict:
    """🔒 SEALED: Orchestrates your existing modules behind the scenes"""
    # 1. Safety first (using your existing safety module)
    cleaned_prompt = safety_scrub(request['prompt'])
    
    # 2. Use your existing prompt analysis
    intent = analyze_prompt_style(cleaned_prompt)
    
    # 3. Use your existing prompt building
    positive, negative = build_prompts(cleaned_prompt, intent)
    
    # 4. Use your existing settings system
    base_settings = build_settings(request['package_goal'], intent)
    
    # 5. Use your existing resource validation
    resources = validate_resources(request.get('resources', []))
    
    # 6. Use your existing caption system
    captions = generate_captions(cleaned_prompt, request.get('caption'))
    
    # 7. NEW: Generate workflow patches (minimal addition)
    workflow_patch = generate_workflow_patch(base_settings)
    
    # 8. Return sealed package - no internal reasoning exposed
    return {
        "package_version": "v1.0",
        "positive": positive,
        "negative": negative,
        "config": base_settings,
        "workflow_patch": workflow_patch,
        "safety": {"status": "cleaned", "resources": resources},
        "menus": _get_menus(request['package_goal']),
        "package_goal": request['package_goal']
    }

def _get_menus(package_goal: str) -> list:
    """Get appropriate menus for the package goal"""
    base_menus = ["variants", "prompt", "negatives", "config", "workflow", "version", "rationale", "discard", "help"]
    
    # Add goal-specific menus
    if package_goal in ["i2i", "i2v"]:
        base_menus.append("denoise")
    if package_goal in ["t2v", "i2v"]:
        base_menus.extend(["frames", "motion"])
        
    return base_menus
