# forge_prompts.py
def build_prompts(prompt, profile=None):
    """
    Build positive and negative prompts.
    Profile can later add CASE alignment and adaptivity.
    """
    positive = f"{prompt}, ultra-detailed, cinematic, 4k"
    negative = "blurry, low quality, watermark, distorted anatomy, duplicate limbs, artifacts"
    return positive, negative
