# forge_integrations.py

def list_integrations(active_only=True):
    """
    List ecosystem integrations.
    Future: activate/deactivate dynamically.
    """
    integrations = {
        "huggingface": {"status": "available", "url": "https://huggingface.co"},
        "civitai": {"status": "available", "url": "https://civitai.com"},
        "comfyui-connect": {"status": "planned", "url": None},
        "arxiv": {"status": "planned", "url": None},
        "reddit": {"status": "planned", "url": None},
        "x-platform": {"status": "planned", "url": None}
    }

    if active_only:
        return {k: v for k, v in integrations.items() if v["status"] == "available"}
    return integrations
