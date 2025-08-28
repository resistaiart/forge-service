# forge_captions.py

def generate_captions(prompt, caption=None, profile=None):
    """
    Generate captions in multiple tones: Hook, Narrative, Technical.
    """
    return {
        "hook": f"{prompt} ⚔️ Neon skies. Future forged.",
        "narrative": f"A cinematic artwork of {prompt}, optimised with The Forge settings for clarity and impact.",
        "technical": f"Prompt engineered with weighted emphasis, tuned CFG, and validated resources. Designed for ComfyUI reproducibility.",
        "alt_text": f"Artwork depicting {prompt.lower()}, cinematic style.",
        "hashtags": "#AIart #ComfyUI #StableDiffusion #TheForge"
    }
