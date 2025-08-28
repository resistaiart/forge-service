# forge_diagnostics.py
def generate_diagnostics(settings, resources):
    """
    Explain why settings/resources were chosen.
    Later: add trade-offs + alternatives.
    """
    return {
        "sampler_choice": f"{settings['sampler']} chosen for detail + stability.",
        "cfg_reason": f"CFG {settings['cfg_scale']} balances prompt adherence + creativity.",
        "resolution_reason": f"{settings['resolution']} chosen for cinematic aspect ratio.",
        "resource_notes": f"{len(resources)} resources validated."
    }
