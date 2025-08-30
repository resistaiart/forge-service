# forge_comfy_patches.py
# 🔒 PRIVATE IMPLEMENTATION - Generates ComfyUI JSON patches
# Does NOT conflict with forge_workflows.py

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


def generate_workflow_patch(settings: Dict[str, Any]) -> Dict[str, Any]:
    """
    🔒 SEALED: Generates minimal ComfyUI workflow patches based on settings.
    Creates diff-style patches for KSampler, EmptyLatentImage, etc.

    Supported settings:
        - sampler (str)
        - steps (int)
        - cfg_scale (float)
        - seed (int)
        - resolution (str, e.g. "832x1216")
        - denoise (float)
    """
    patch = {"nodes": []}

    # KSampler configuration
    sampler_params = {}
    if "sampler" in settings:
        sampler_params["sampler_name"] = settings["sampler"]
    if "steps" in settings:
        sampler_params["steps"] = settings["steps"]
    if "cfg_scale" in settings:
        sampler_params["cfg"] = settings["cfg_scale"]
    if "seed" in settings:
        sampler_params["seed"] = settings["seed"]

    if sampler_params:
        patch["nodes"].append({
            "op": "set",
            "node": "KSampler",
            "params": sampler_params
        })

    # Resolution configuration
    if "resolution" in settings and settings["resolution"] != "match_input":
        try:
            width, height = map(int, settings["resolution"].split("x"))
            patch["nodes"].append({
                "op": "set",
                "node": "EmptyLatentImage",
                "params": {"width": width, "height": height}
            })
        except ValueError:
            logger.warning(f"Invalid resolution format: {settings['resolution']} (expected 'WxH')")

    # Denoise strength for I2I/I2V
    if "denoise" in settings:
        patch["nodes"].append({
            "op": "set",
            "node": "KSampler",  # ComfyUI expects this on KSampler
            "params": {"denoise": settings["denoise"]}
        })

    return patch
