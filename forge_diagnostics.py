# forge_diagnostics.py

def generate_diagnostics(settings, resources):
    """
    Explain why each choice was made + what alternatives exist.
    """
    return {
        "sampler_choice": f"{settings['sampler']} selected for neon light stability. Alternative: Euler a (faster, less precise).",
        "cfg_reason": f"CFG {settings['cfg_scale']} balances prompt adherence + creativity. Higher values risk oversaturation.",
        "resolution_reason": f"{settings['resolution']} ensures cinematic ratio. Alternative: 1024x1024 square framing.",
        "resource_notes": f"{len(resources)} resources validated, {sum(1 for r in resources if r['status'] != 'Verified')} flagged."
    }
