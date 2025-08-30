# forge/profiles.py
import json
import os
from typing import Dict, Any, Optional, List
from pathlib import Path
import logging
from enum import Enum
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class VerbosityLevel(Enum):
    COMPACT = "compact"
    NORMAL = "normal"
    VERBOSE = "verbose"


class CaptionStyle(Enum):
    BALANCED = "balanced"
    TECHNICAL = "technical"
    NARRATIVE = "narrative"
    ACCESSIBILITY = "accessibility"


class CheckpointPreference(Enum):
    QUALITY = "quality"
    SPEED = "speed"
    BALANCED = "balanced"
    CUSTOM = "custom"


DEFAULT_PROFILE = {
    "verbosity": VerbosityLevel.NORMAL.value,
    "caption_style": CaptionStyle.BALANCED.value,
    "checkpoint_preference": CheckpointPreference.BALANCED.value,
    "preferred_checkpoint": "forge-base-v1.safetensors",
    "preferred_sampler": "DPM++ 2M Karras",
    "preferred_scheduler": "Karras",
    "default_cfg_scale": 7.5,
    "default_steps": 28,
    "style_boost": {
        "realistic": {"cfg_adjust": -0.5, "steps_adjust": 5},
        "anime": {"cfg_adjust": 0.5, "steps_adjust": -3},
        "cyberpunk": {"cfg_adjust": 1.0, "steps_adjust": 2},
        "fantasy": {"cfg_adjust": 0.5, "steps_adjust": 2},
    },
    "content_preferences": {
        "allow_nsfw": False,
        "preferred_aspect_ratios": ["16:9", "1:1", "9:16"],
        "max_output_size": "1024x1024",
    },
    "metadata": {
        "created": datetime.now(timezone.utc).isoformat(),
        "last_modified": datetime.now(timezone.utc).isoformat(),
        "usage_count": 0,
    },
}

_profile_store: Dict[str, Dict[str, Any]] = {"default": DEFAULT_PROFILE.copy()}
PROFILES_DIR = Path(os.getenv("FORGE_PROFILES_DIR", "./profiles"))


def _ensure_profiles_dir():
    PROFILES_DIR.mkdir(exist_ok=True, parents=True)


def load_profile(user_id: str = "default") -> Dict[str, Any]:
    """Load profile from memory or disk."""
    if user_id in _profile_store:
        return _profile_store[user_id].copy()

    profile_path = PROFILES_DIR / f"{user_id}.json"
    if profile_path.exists():
        try:
            with open(profile_path, "r") as f:
                profile = json.load(f)
            _profile_store[user_id] = profile
            logger.info(f"Loaded profile for user '{user_id}' from disk")
            return profile.copy()
        except Exception as e:
            logger.warning(f"Failed to load profile for '{user_id}': {e}", exc_info=True)

    logger.info(f"Using default profile for user '{user_id}'")
    return DEFAULT_PROFILE.copy()


def save_profile(user_id: str, profile: Dict[str, Any]) -> bool:
    """Save profile to disk and memory."""
    try:
        _ensure_profiles_dir()
        profile_path = PROFILES_DIR / f"{user_id}.json"

        meta = profile.get("metadata", {})
        now = datetime.now(timezone.utc).isoformat()

        # Preserve creation date if present
        created = meta.get("created", now)
        usage_count = meta.get("usage_count", 0) + 1

        profile_with_meta = profile.copy()
        profile_with_meta["metadata"] = {
            "created": created,
            "last_modified": now,
            "usage_count": usage_count,
        }

        with open(profile_path, "w") as f:
            json.dump(profile_with_meta, f, indent=2)

        _profile_store[user_id] = profile_with_meta
        logger.info(f"Saved profile for user '{user_id}'")
        return True
    except Exception as e:
        logger.error(f"Failed to save profile for '{user_id}': {e}", exc_info=True)
        return False


def update_profile(user_id: str = "default", updates: Optional[Dict[str, Any]] = None) -> bool:
    if not updates:
        return False
    profile = load_profile(user_id)
    profile.update(updates)
    return save_profile(user_id, profile)


def create_profile(user_id: str, base_profile: Optional[Dict[str, Any]] = None) -> bool:
    if user_id in _profile_store:
        logger.warning(f"Profile already exists for user '{user_id}'")
        return False
    profile = base_profile.copy() if base_profile else DEFAULT_PROFILE.copy()
    return save_profile(user_id, profile)


def adapt_settings(settings: Dict[str, Any], profile: Dict[str, Any]) -> Dict[str, Any]:
    """Adjust generation settings according to profile."""
    settings = settings.copy()

    verbosity = profile.get("verbosity", VerbosityLevel.NORMAL.value)
    if verbosity == VerbosityLevel.VERBOSE.value:
        settings["steps"] = settings.get("steps", 20) + 8
    elif verbosity == VerbosityLevel.COMPACT.value:
        settings["steps"] = max(15, settings.get("steps", 20) - 5)

    detected_style = settings.get("detected_style")
    style_boost = profile.get("style_boost", {})
    if detected_style and detected_style in style_boost:
        boost = style_boost[detected_style]
        settings["cfg_scale"] = settings.get("cfg_scale", 7.5) + boost.get("cfg_adjust", 0)
        settings["steps"] = settings.get("steps", 20) + boost.get("steps_adjust", 0)

    caption_style = profile.get("caption_style", CaptionStyle.BALANCED.value)
    if caption_style == CaptionStyle.TECHNICAL.value:
        settings["cfg_scale"] = settings.get("cfg_scale", 7.5) + 0.7

    settings["cfg_scale"] = max(1.0, min(20.0, settings.get("cfg_scale", 7.5)))
    settings["steps"] = max(10, min(100, settings.get("steps", 20)))

    return settings


def adapt_captions(captions: Dict[str, str], profile: Dict[str, Any]) -> Dict[str, str]:
    """Adapt captions according to profile."""
    captions = captions.copy()
    style = profile.get("caption_style", CaptionStyle.BALANCED.value)

    if style == CaptionStyle.TECHNICAL.value:
        captions["narrative"] = f"[Technical Analysis] {captions.get('narrative', '')}"
        captions["hook"] = f"Technical Overview: {captions.get('hook', '')}"
    elif style == CaptionStyle.NARRATIVE.value:
        captions["narrative"] = f"[Story] {captions.get('narrative', '')}"
        captions["hook"] = f"Story: {captions.get('hook', '')}"
    elif style == CaptionStyle.ACCESSIBILITY.value:
        captions["narrative"] = f"[Accessibility] {captions.get('narrative', '')}"
        if "alt_text" in captions:
            captions["alt_text"] = f"Detailed description: {captions['alt_text']}"

    return captions


def get_profile_stats() -> Dict[str, Any]:
    _ensure_profiles_dir()
    profile_files = list(PROFILES_DIR.glob("*.json"))
    return {
        "total_profiles": len(_profile_store),
        "saved_profiles": len(profile_files),
        "default_profile_uses": _profile_store.get("default", {}).get("metadata", {}).get("usage_count", 0),
    }


def list_profiles() -> List[str]:
    return list(_profile_store.keys())


def delete_profile(user_id: str) -> bool:
    try:
        if user_id in _profile_store:
            del _profile_store[user_id]
        profile_path = PROFILES_DIR / f"{user_id}.json"
        if profile_path.exists():
            profile_path.unlink()
        logger.info(f"Deleted profile for user '{user_id}'")
        return True
    except Exception as e:
        logger.error(f"Failed to delete profile for '{user_id}': {e}", exc_info=True)
        return False
