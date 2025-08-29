### Enhanced `forge_captions.py`

```python
# forge_captions.py
import re
import random
from typing import Dict, List, Optional
from enum import Enum

class CaptionStyle(Enum):
    HOOK = "hook"
    NARRATIVE = "narrative"
    TECHNICAL = "technical"
    ACCESSIBILITY = "accessibility"
    SOCIAL = "social"
    MINIMAL = "minimal"

class Tone(Enum):
    NEUTRAL = "neutral"
    DRAMATIC = "dramatic"
    TECHNICAL = "technical"
    STORYTELLING = "storytelling"
    PROMOTIONAL = "promotional"

# Template library for different caption styles
CAPTION_TEMPLATES = {
    CaptionStyle.HOOK: {
        Tone.NEUTRAL: [
            "✨ {prompt} - Crafted with precision",
            "🎨 {prompt} - AI artistry redefined",
            "⚡ {prompt} - Forged in digital fire"
        ],
        Tone.DRAMATIC: [
            "🔥 {prompt} - Witness the future of creation",
            "⚔️ {prompt} - Where art meets algorithm",
            "🌌 {prompt} - Beyond imagination, rendered real"
        ],
        Tone.PROMOTIONAL: [
            "🚀 {prompt} - Experience next-gen AI art",
            "🎯 {prompt} - Precision-engineered creativity",
            "💎 {prompt} - Premium AI artistry unleashed"
        ]
    },
    CaptionStyle.NARRATIVE: {
        Tone.STORYTELLING: [
            "This artwork tells the story of {prompt}, brought to life through advanced AI synthesis",
            "A visual narrative exploring {prompt}, created with cutting-edge generative technology",
            "In this scene: {prompt}. A moment captured through computational creativity"
        ],
        Tone.DRAMATIC: [
            "Behold {prompt} - a dramatic vision forged in latent space",
            "Epic portrayal of {prompt}, rendered with cinematic intensity",
            "Grand vision of {prompt}, realized through algorithmic artistry"
        ]
    },
    CaptionStyle.TECHNICAL: {
        Tone.TECHNICAL: [
            "Technical breakdown: {prompt} | Optimized CFG: {cfg} | Steps: {steps} | Sampler: {sampler}",
            "AI Art Specification: {prompt} | Engineered with weighted emphasis and precision sampling",
            "Render Config: {prompt} | Validated resources + tuned parameters for optimal output"
        ]
    },
    CaptionStyle.ACCESSIBILITY: {
        Tone.NEUTRAL: [
            "Digital artwork depicting {prompt}. {details}",
            "AI-generated image showing {prompt}. Visual elements include {details}",
            "Computer-generated artwork featuring {prompt}. Composition includes {details}"
        ]
    }
}

# Hashtag collections
HASHTAG_SETS = {
    "default": ["AIart", "ComfyUI", "StableDiffusion", "TheForge", "GenerativeAI"],
    "technical": ["AIEngineering", "PromptDesign", "SDXL", "DiffusionModel", "TechArt"],
    "creative": ["DigitalArt", "CreativeAI", "ArtisticAI", "FutureArt", "NeoArt"],
    "community": ["AIArtCommunity", "GenAI", "MachineLearningArt", "ComputationalCreativity"]
}

def generate_captions(prompt: str, caption: Optional[str] = None, 
                     profile: Optional[Dict] = None) -> Dict[str, str]:
    """
    Generate comprehensive captions in multiple styles and tones.
    
    Args:
        prompt: The main prompt/description of the content
        caption: Optional additional context or existing caption
        profile: User profile containing preferences and style settings
    
    Returns:
        Dictionary of captions for different purposes
    """
    if profile is None:
        profile = {}
    
    # Use provided caption or generate from prompt
    description = caption if caption else prompt
    tone = profile.get("tone", Tone.NEUTRAL.value)
    style_preference = profile.get("caption_style", "balanced")
    
    # Extract key elements for more intelligent captioning
    prompt_elements = _analyze_prompt(prompt)
    
    # Generate each caption type
    captions = {
        "hook": _generate_hook(description, tone, prompt_elements),
        "narrative": _generate_narrative(description, tone, prompt_elements),
        "technical": _generate_technical(description, prompt_elements, profile),
        "alt_text": _generate_alt_text(description, prompt_elements),
        "social": _generate_social(description, tone),
        "hashtags": _generate_hashtags(prompt_elements, style_preference),
        "metadata": _generate_metadata(prompt, profile)
    }
    
    # Apply profile-based adaptations
    captions = _apply_profile_adaptations(captions, profile)
    
    return captions

def _analyze_prompt(prompt: str) -> Dict[str, List[str]]:
    """Analyze prompt to extract key elements for better caption generation."""
    prompt_lower = prompt.lower()
    
    # Simple analysis - can be enhanced with NLP later
    elements = {
        "subjects": [],
        "styles": [],
        "moods": [],
        "environments": [],
        "keywords": prompt.split()[:10]  # First 10 words as keywords
    }
    
    # Basic keyword detection (can be expanded)
    style_keywords = ["cyberpunk", "realistic", "anime", "fantasy", "cinematic", "painting"]
    mood_keywords = ["epic", "dark", "bright", "mysterious", "serene", "dramatic"]
    environment_keywords = ["landscape", "portrait", "city", "nature", "space", "interior"]
    
    for word in prompt_lower.split():
        if word in style_keywords:
            elements["styles"].append(word)
        elif word in mood_keywords:
            elements["moods"].append(word)
        elif word in environment_keywords:
            elements["environments"].append(word)
        elif len(word) > 5:  # Longer words are likely subjects
            elements["subjects"].append(word)
    
    return elements

def _generate_hook(description: str, tone: str, elements: Dict) -> str:
    """Generate an engaging hook caption."""
    tone_enum = Tone(tone) if tone in [t.value for t in Tone] else Tone.NEUTRAL
    templates = CAPTION_TEMPLATES[CaptionStyle.HOOK].get(tone_enum, CAPTION_TEMPLATES[CaptionStyle.HOOK][Tone.NEUTRAL])
    
    template = random.choice(templates)
    return template.format(prompt=description, mood=elements.get("moods", ["epic"])[0])

def _generate_narrative(description: str, tone: str, elements: Dict) -> str:
    """Generate a narrative description."""
    tone_enum = Tone(tone) if tone in [t.value for t in Tone] else Tone.NEUTRAL
    templates = CAPTION_TEMPLATES[CaptionStyle.NARRATIVE].get(tone_enum, CAPTION_TEMPLATES[CaptionStyle.NARRATIVE][Tone.STORYTELLING])
    
    template = random.choice(templates)
    return template.format(prompt=description)

def _generate_technical(description: str, elements: Dict, profile: Dict) -> str:
    """Generate a technical description."""
    technical_details = {
        "prompt": description,
        "cfg": profile.get("default_cfg_scale", "7.5"),
        "steps": profile.get("default_steps", "28"),
        "sampler": profile.get("preferred_sampler", "DPM++ 2M Karras")
    }
    
    template = random.choice(CAPTION_TEMPLATES[CaptionStyle.TECHNICAL][Tone.TECHNICAL])
    return template.format(**technical_details)

def _generate_alt_text(description: str, elements: Dict) -> str:
    """Generate accessibility-friendly alt text."""
    subjects = elements.get("subjects", [])
    styles = elements.get("styles", [])
    
    if subjects and styles:
        alt_text = f"{' '.join(styles)} style artwork depicting {', '.join(subjects[:3])}"
    else:
        alt_text = f"AI-generated artwork showing {description.lower()}"
    
    return alt_text + ". Digital art created with generative AI."

def _generate_social(description: str, tone: str) -> str:
    """Generate social media optimized caption."""
    emojis = {
        Tone.NEUTRAL: "✨🎨⚡",
        Tone.DRAMATIC: "🔥⚔️🌌",
        Tone.PROMOTIONAL: "🚀🎯💎"
    }
    
    emoji_set = emojis.get(Tone(tone), emojis[Tone.NEUTRAL])
    return f"{emoji_set} {description} {emoji_set}"

def _generate_hashtags(elements: Dict, style: str) -> str:
    """Generate relevant hashtags."""
    base_tags = HASHTAG_SETS["default"]
    
    # Add style-specific tags
    if style == "technical":
        base_tags.extend(HASHTAG_SETS["technical"])
    elif style == "creative":
        base_tags.extend(HASHTAG_SETS["creative"])
    
    # Add tags based on content
    if elements.get("styles"):
        base_tags.extend([f"#{s}" for s in elements["styles"][:2]])
    
    return " ".join([f"#{tag}" for tag in base_tags[:8]])  # Limit to 8 hashtags

def _generate_metadata(prompt: str, profile: Dict) -> str:
    """Generate metadata description."""
    return f"Prompt: {prompt} | Profile: {profile.get('verbosity', 'normal')} | Style: {profile.get('caption_style', 'balanced')}"

def _apply_profile_adaptations(captions: Dict[str, str], profile: Dict) -> Dict[str, str]:
    """Apply profile-based adaptations to captions."""
    style = profile.get("caption_style", "balanced")
    
    if style == "technical":
        captions["narrative"] = f"[Technical Analysis] {captions['narrative']}"
        captions["hook"] = f"Technical Overview: {captions['hook']}"
    elif style == "narrative":
        captions["narrative"] = f"[Story] {captions['narrative']}"
        captions["hook"] = f"Story: {captions['hook']}"
    
    return captions

# Backward compatibility function
def generate_captions_legacy(prompt, caption=None, profile=None):
    """Legacy function signature for backward compatibility."""
    return generate_captions(prompt, caption, profile)

# Example usage
if __name__ == "__main__":
    # Test with different prompts and profiles
    test_prompt = "cyberpunk samurai in neon-lit Tokyo streets"
    
    print("=== Default Captions ===")
    captions = generate_captions(test_prompt)
    for key, value in captions.items():
        print(f"{key}: {value}")
    
    print("\n=== Technical Profile ===")
    tech_profile = {"caption_style": "technical", "tone": "technical"}
    tech_captions = generate_captions(test_prompt, profile=tech_profile)
    for key, value in tech_captions.items():
        print(f"{key}: {value}")
```
