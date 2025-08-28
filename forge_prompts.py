# forge_prompts.py

# Libraries of styles and negatives
NEGATIVES = {
    "general": "blurry, low quality, watermark, artifacts, cropped, text",
    "anatomy": "bad anatomy, extra limbs, fused fingers, distorted hands, deformed face",
    "nsfw": "child, underage, gore, rape, snuff, real-world exploitation"
}

STYLE_LIBRARIES = {
    "cinematic": ["cinematic composition", "dramatic lighting", "8k masterpiece", "photorealistic details"],
    "anime": ["anime style", "vibrant cel shading", "clean linework", "studio quality"],
    "artistic": ["oil painting", "brush strokes", "concept art", "artstation trending"],
    "sci-fi": ["futuristic", "cyberpunk atmosphere", "glowing neon lights", "tech noir aesthetic"]
}

def build_prompts(prompt, profile=None, checkpoint="forge-base-v1.safetensors"):
    """
    Builds Positive + Negative prompts with weighting, style adaptation,
    and CASE alignment based on checkpoint type.
    """
    # Base positive prompt with weighted emphasis
    positive = f"(( {prompt}:1.3 )), hyper-detailed, professional composition"

    # Choose style terms based on checkpoint
    if "anime" in checkpoint.lower():
        styles = STYLE_LIBRARIES["anime"]
    elif "realistic" in checkpoint.lower() or "photoreal" in checkpoint.lower():
        styles = STYLE_LIBRARIES["cinematic"]
    else:
        styles = STYLE_LIBRARIES["sci-fi"]

    # Merge styles into positive prompt
    positive += ", " + ", ".join(styles[:3])

    # Build negative prompt dynamically
    negative = NEGATIVES["general"] + ", " + NEGATIVES["anatomy"]

    return positive, negative
