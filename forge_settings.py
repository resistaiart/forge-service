# forge_settings.py
import random

def build_settings(profile=None):
    """
    Build reproducible settings. Later can adjust based on profile.
    """
    return {
        "checkpoint": "forge-base-v1.safetensors [Verified]",
        "sampler": "DPM++ 2M Karras",
        "steps": 28,
        "cfg_scale": 7.5,
        "resolution": "768x1152",
        "scheduler": "Karras",
        "seed": random.randint(100000, 999999),
        "denoise": 0.25
    }
