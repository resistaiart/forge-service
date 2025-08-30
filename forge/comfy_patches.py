# forge/comfy_patches.py
# 🔒 PRIVATE IMPLEMENTATION - Generates ComfyUI JSON patches

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


def generate_workflow_patch(settings: Dict[str, Any]) -> Dict[str, Any]:
    """
    🔒 SEALED: Generates ComfyUI workflow patches from Forge settings.
    Creates diff-style patches for KSampler, EmptyLatentImage, etc.

    Supported settings:
        - sampler, scheduler
        - steps, cfg_scale, seed
        - batch_size, clip_skip
        - resolution (e.g. "832x1216", skip if "match_input")
        - denoise
    """
    patch = {"nodes": []}

    # KSampler node
    sampler_params = {}
    mapping = {
        "sampler": "sampler_name",
        "scheduler": "scheduler",
        "steps": "steps",
        "cfg_scale": "cfg",
        "seed": "seed",
        "batch_size": "batch_size",
        "clip_skip": "clip_skip",
        "denoise": "denoise",
    }

    for key, target in mapping.items():
        if key in settings and settings[key] is not None:
            sampler_params[target] = settings[key]

    if sampler_params:
        patch["nodes"].append({
            "op": "set",
            "node": "KSampler",
            "params": sampler_params
        })

    # Resolution node
    if "resolution" in settings and settings["resolution"] != "match_input":
        try:
            width, height = map(int, settings["resolution"].split("x"))
            patch["nodes"].append({
                "op": "set",
                "node": "EmptyLatentImage",
                "params": {"width": width, "height": height}
            })
        except Exception:
            logger.warning(f"Invalid resolution format: {settings['resolution']} (expected 'WxH')")

    return patch
