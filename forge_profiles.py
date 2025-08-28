# forge_profiles.py
# For simplicity we’ll just keep one profile in memory for now.
# Later: replace with DB or per-user JSON files.

_profile_store = {
    "default": {
        "verbosity": "normal",
        "caption_style": "balanced",
        "preferred_checkpoint": "forge-base-v1.safetensors"
    }
}

def load_profile(user_id="default"):
    return _profile_store.get(user_id, _profile_store["default"])

def update_profile(user_id="default", profile=None):
    if profile:
        _profile_store[user_id] = profile
