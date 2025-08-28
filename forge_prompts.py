# forge_prompts.py
import re
import random

# ---- Core Utilities ----
def clean_prompt(prompt: str) -> str:
    """Sanitize and normalize a raw prompt string."""
    return re.sub(r"\s+", " ", prompt.strip())

def extract_keywords(prompt: str) -> list:
    """Extract keywords (skip stop words, remove duplicates)."""
    stop_words = {"a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for"}
    words = prompt.lower().split()
    return list({w for w in words if w not in stop_words and len(w) > 3})

def validate_prompt(prompt: str) -> dict:
    """Validate prompt quality and return issues."""
    issues, words = [], prompt.split()
    if len(prompt) < 5: issues.append("Prompt too short")
    if len(prompt) > 500: issues.append("Prompt too long")
    if len(words) < 3: issues.append("Prompt lacks descriptive terms")
    return {"valid": not issues, "issues": issues, "word_count": len(words), "char_count": len(prompt)}

# ---- Keyword Weighting ----
def weight_keywords(prompt: str, custom_weights: dict = None) -> str:
    """Add emphasis weighting to important words."""
    default_weights = {
        "cyberpunk": 1.3, "samurai": 1.3, "neon": 1.2,
        "cinematic": 1.4, "ultra-detailed": 1.5,
        "portrait": 1.2, "landscape": 1.2,
        "anime": 1.3, "fantasy": 1.3, "realistic": 1.4
    }
    weights = {**default_weights, **(custom_weights or {})}
    for word, w in weights.items():
        prompt = re.sub(rf"\b{re.escape(word)}\b", f"(({word}:{w}))", prompt, flags=re.IGNORECASE)
    return prompt

# ---- Intent Analysis ----
def analyze_prompt_intent(prompt: str) -> dict:
    """Detect style, mood, composition intent from keywords."""
    intent = {"style": "realistic", "mood": "neutral", "composition": "general", "lighting": "natural"}
    style_map = {
        "cyberpunk": ["cyberpunk", "neon", "futuristic"],
        "anime": ["anime", "manga", "cel-shaded"],
        "fantasy": ["fantasy", "magical", "dragon"],
        "realistic": ["photorealistic", "realistic", "photo"]
    }
    pl = prompt.lower()
    for style, kws in style_map.items():
        if any(k in pl for k in kws): intent["style"] = style; break
    if any(w in pl for w in ["dark", "gloomy", "sinister"]): intent["mood"] = "dark"
    elif any(w in pl for w in ["bright", "happy", "vibrant"]): intent["mood"] = "bright"
    return intent

# ---- Dynamic Settings ----
def get_optimized_settings(goal: str, intent: dict) -> dict:
    """Return generation settings tuned to goal + intent."""
    base = {
        "t2i": {"cfg_scale": 7.5, "steps": 28, "resolution": "832x1216", "sampler": "DPM++ 2M Karras", "scheduler": "Karras"},
        "t2v": {"cfg_scale": 8.5, "steps": 35, "resolution": "768x768", "sampler": "DPM++ 2M Karras", "scheduler": "Karras"}
    }
    settings = base.get(goal, base["t2i"]).copy()
    adjust = {
        "realistic": {"cfg_scale": 7.0, "steps": 32},
        "anime": {"cfg_scale": 8.0, "denoise": 0.3},
        "cyberpunk": {"cfg_scale": 8.5, "steps": 30},
        "fantasy": {"cfg_scale": 8.0, "denoise": 0.35}
    }
    if intent["style"] in adjust: settings.update(adjust[intent["style"]])
    settings["seed"] = random.randint(1, 999999999)
    return settings

# ---- Negative Prompts ----
def get_negative_prompt(intent: dict) -> str:
    """Context-aware negatives (avoid unwanted styles)."""
    base = "blurry, low quality, watermark, artifacts, cropped, text, bad anatomy, extra limbs, fused fingers, distorted hands, deformed face"
    style_neg = {
        "realistic": "3d render, cartoon, anime, painting, drawing",
        "anime": "realistic, photorealistic, 3d render, western animation",
        "cyberpunk": "historical, medieval, rustic, vintage, antique",
        "fantasy": "modern, contemporary, urban, technological"
    }
    return base + (", " + style_neg[intent["style"]] if intent["style"] in style_neg else "")

# ---- Main Builder ----
def optimise_prompt_package(prompt: str, goal: str = "t2i", resources: list = None, caption: str = None) -> dict:
    """Forge optimised prompt package for [t2i] or [t2v]."""
    cleaned = clean_prompt(prompt)
    intent = analyze_prompt_intent(cleaned)
    weighted = weight_keywords(cleaned)
    negative = get_negative_prompt(intent)
    settings = get_optimized_settings(goal, intent)

    diagnostics = {
        "cfg_reason": f"CFG {settings['cfg_scale']} optimised for {intent['style']} style",
        "sampler_choice": f"{settings['sampler']} selected for stability in {intent['style']}",
        "resolution_reason": f"{settings['resolution']} tuned for {goal} output",
        "detected_style": intent["style"],
        "detected_mood": intent["mood"]
    }

    return {
        "goal": goal,
        "positive_prompt": weighted,
        "negative_prompt": negative,
        "settings": settings,
        "resources": resources or [],
        "caption": caption,
        "profile_used": {"verbosity": "normal", "caption_style": "balanced", "preferred_checkpoint": "forge-base-v1.safetensors"},
        "diagnostics": diagnostics,
        "intent_analysis": intent,
        "validation": validate_prompt(cleaned)
    }
