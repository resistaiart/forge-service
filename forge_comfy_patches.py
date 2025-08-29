# forge_comfy_patches.py
# 🔒 PRIVATE IMPLEMENTATION - Generates ComfyUI JSON patches
# Does NOT conflict with forge_workflows.py

def generate_workflow_patch(settings: Dict[str, Any]) -> Dict[str, Any]:
    """
    🔒 SEALED: Generates minimal ComfyUI workflow patches based on settings.
    Creates diff-style patches for KSampler, EmptyLatentImage, etc.
    """
    patch = {"nodes": []}

    # KSampler configuration
    if "sampler" in settings or "steps" in settings or "cfg_scale" in settings:
        sampler_params = {}
        if "sampler" in settings:
            sampler_params["sampler_name"] = settings["sampler"]
        if "steps" in settings:
            sampler_params["steps"] = settings["steps"]
        if "cfg_scale" in settings:
            sampler_params["cfg"] = settings["cfg_scale"]
        if "seed" in settings:
            sampler_params["seed"] = settings["seed"]

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
        except:
            # Fallback if resolution format is invalid
            pass

    # Denoise strength for I2I/I2V
    if "denoise" in settings:
        patch["nodes"].append({
            "op": "set",
            "node": "KSampler",  # or specific node for denoise
            "params": {"denoise": settings["denoise"]}
        })

    return patch
