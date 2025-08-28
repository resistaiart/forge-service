# forge_captions.py
def generate_captions(prompt, caption=None, profile=None):
    """
    Generate multiple caption variants.
    Later: add adaptivity + social optimisation.
    """
    return {
        "hook": f"{prompt} ⚔️🔥",
        "narrative": f"A cinematic rendering of {prompt}.",
        "alt_text": f"Artwork of {prompt.lower()}",
        "hashtags": "#AIart #ComfyUI #TheForge #StableDiffusion"
    }
