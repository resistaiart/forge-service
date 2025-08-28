# forge_profiles.py

_profile_store = {
    "default": {
        "verbosity": "normal",  # compact, normal, verbose
        "caption_style": "balanced",  # balanced, technical, narrative
        "preferred_checkpoint": "forge-base-v1.safetensors"
    }
}

def load_profile(user_id="default"):
    """
    Load user profile. Defaults if not found.
    """
    return _profile_store.get(user_id, _profile_store["default"])

def update_profile(user_id="default", profile=None):
    """
    Update stored profile. 
    Future: could persist to DB or JSON file.
    """
    if profile:
        _profile_store[user_id] = profile

def adapt_settings(settings, profile):
    """
    Adapt settings based on profile preferences.
    """
    if profile.get("verbosity") == "verbose":
        settings["steps"] += 5
    if profile.get("caption_style") == "technical":
        settings["cfg_scale"] += 0.5
    return settings

def adapt_captions(captions, profile):
    """
    Adapt captions tone based on profile preference.
    """
    style = profile.get("caption_style", "balanced")
    if style == "technical":
        captions["narrative"] = f"[TECHNICAL] {captions['narrative']}"
    elif style == "narrative":
        captions["narrative"] = f"[STORY] {captions['narrative']}"
    return captions
