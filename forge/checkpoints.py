# forge/checkpoints.py
import logging
from typing import Dict, List, Optional, Any
from enum import Enum

logger = logging.getLogger(__name__)


class CheckpointSource(Enum):
    CIVITAI = "civitai"
    HUGGINGFACE = "huggingface"
    LOCAL = "local"
    FORGE = "forge"


class CheckpointType(Enum):
    BASE = "base"
    INPAINTING = "inpainting"
    ANIME = "anime"
    REALISTIC = "realistic"
    SPECIALIZED = "specialized"
    VIDEO = "video"
    UPSCALE = "upscale"


def suggest_checkpoints(
    preferred_checkpoint: Optional[str] = None,
    prompt: Optional[str] = None,
    goal: str = "t2i",
) -> List[Dict[str, Any]]:
    """
    Suggest appropriate model checkpoints based on prompt and goal.
    Returns a list of recommended checkpoint configurations.
    """
    forge_checkpoints = [
        {
            "name": "forge-base-v1.safetensors",
            "source": CheckpointSource.FORGE.value,
            "type": CheckpointType.BASE.value,
            "recommended_for": ["general", "balanced", "t2i"],
            "resolution": "832x1216",
            "default_cfg": 7.5,
            "default_steps": 28,
            "priority": 1,
        },
        {
            "name": "forge-animate-v1.safetensors",
            "source": CheckpointSource.FORGE.value,
            "type": CheckpointType.VIDEO.value,
            "recommended_for": ["video", "animation", "t2v", "i2v"],
            "resolution": "768x768",
            "default_cfg": 8.5,
            "default_steps": 35,
            "priority": 1,
        },
        {
            "name": "forge-upscale-v1.safetensors",
            "source": CheckpointSource.FORGE.value,
            "type": CheckpointType.UPSCALE.value,
            "recommended_for": ["upscaling", "detail-enhancement"],
            "resolution": "1024x1024",
            "default_cfg": 6.0,
            "default_steps": 20,
            "priority": 1,
        },
    ]

    # Specific checkpoint requested → prioritise
    if preferred_checkpoint:
        for checkpoint in forge_checkpoints:
            if checkpoint["name"] == preferred_checkpoint:
                checkpoint["priority"] = 0
                return [checkpoint] + [
                    c for c in forge_checkpoints if c["name"] != preferred_checkpoint
                ]

    # Sort by priority → then relevance to goal → then name
    sorted_checkpoints = sorted(
        forge_checkpoints,
        key=lambda x: (
            x["priority"],
            0 if goal in x["recommended_for"] else 1,
            x["name"],
        ),
    )
    return sorted_checkpoints


def get_checkpoint_config(checkpoint_name: str) -> Dict[str, Any]:
    """
    Get specific configuration for a checkpoint.
    """
    all_checkpoints = suggest_checkpoints()

    for checkpoint in all_checkpoints:
        if checkpoint["name"] == checkpoint_name:
            return checkpoint

    # Unknown checkpoint → return fallback
    logger.warning(f"Checkpoint {checkpoint_name} not found. Returning unverified config.")
    return {
        "name": checkpoint_name,
        "source": CheckpointSource.LOCAL.value,
        "type": CheckpointType.BASE.value,
        "recommended_for": ["general"],
        "resolution": "832x1216",
        "default_cfg": 7.5,
        "default_steps": 28,
        "priority": 2,
        "status": "unverified"
    }


def fetch_civitai_metadata(model_id: str) -> Dict[str, Any]:
    """
    Fetch metadata from CivitAI API for a specific model.
    Currently not implemented.
    """
    logger.info(f"fetch_civitai_metadata called for model_id={model_id}, but this is not implemented yet.")
    return {"status": "not_implemented", "model_id": model_id}


def enhance_package_with_checkpoints(package: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enhance a prompt package with checkpoint-specific optimizations.
    """
    checkpoint_name = package.get("settings", {}).get("checkpoint", "forge-base-v1.safetensors")
    checkpoint_config = get_checkpoint_config(checkpoint_name)

    package.setdefault("settings", {})

    # Preserve existing overrides if present
    package["settings"].setdefault("checkpoint", checkpoint_name)
    package["settings"].setdefault("cfg_scale", checkpoint_config.get("default_cfg", 7.5))
    package["settings"].setdefault("steps", checkpoint_config.get("default_steps", 28))
    package["settings"].setdefault("resolution", checkpoint_config.get("resolution", "832x1216"))

    package["checkpoint_metadata"] = checkpoint_config
    return package


if __name__ == "__main__":
    suggestions = suggest_checkpoints(goal="t2v")
    logger.info("Checkpoint suggestions for T2V:")
    for checkpoint in suggestions:
        logger.info(f"  - {checkpoint['name']}: {checkpoint['recommended_for']}")

    config = get_checkpoint_config("forge-animate-v1.safetensors")
    logger.info(f"Config for forge-animate-v1: {config}")
