# forge_settings.py
import random

def build_settings(profile=None, package_goal="image"):
    """
    Builds reproducible settings, tuned per goal type.
    """
    if package_goal in ["t2v", "i2v", "video"]:
        steps = 20
        resolution = "512x512"  # stable baseline for video frames
        cfg = 6.5
    else:  # image
        steps = 30
        resolution = "768x1152"
        cfg = 8.0

    return {
        "checkpoint": profile.get("preferred_checkpoint", "forge-base-v1.safetensors") if profile else "forge-base-v1.safetensors",
        "sampler": "DPM++ 2M Karras",
        "steps": steps,
        "cfg_scale": cfg,
        "resolution": resolution,
        "scheduler": "Karras",
        "seed": random.randint(100000, 999999),
        "denoise": 0.25
    }
