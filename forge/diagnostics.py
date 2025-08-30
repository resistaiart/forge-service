# forge_diagnostics.py
from typing import Dict, List, Any
from enum import Enum
import random
import logging

logger = logging.getLogger(__name__)


class DiagnosticLevel(Enum):
    BASIC = "basic"
    DETAILED = "detailed"
    EXPERT = "expert"


class SettingCategory(Enum):
    SAMPLER = "sampler"
    CFG = "cfg_scale"
    RESOLUTION = "resolution"
    STEPS = "steps"
    SCHEDULER = "scheduler"
    DENOISE = "denoise"
    CHECKPOINT = "checkpoint"


# Knowledge base for diagnostics
DIAGNOSTIC_KNOWLEDGE = {
    SettingCategory.SAMPLER: {
        "DPM++ 2M Karras": {
            "strengths": ["excellent detail", "stable convergence", "good for complex prompts"],
            "weaknesses": ["slower than some alternatives"],
            "alternatives": {
                "Euler a": "faster, more creative but less precise",
                "LMS": "good for smooth results, less detailed",
                "DDIM": "classic, predictable but slower"
            },
            "recommendation": "Ideal for detailed scenes and complex compositions"
        },
        "Euler a": {
            "strengths": ["fast", "creative variations", "good for exploration"],
            "weaknesses": ["less consistent", "can miss details"],
            "alternatives": {
                "DPM++ 2M Karras": "slower but more precise and detailed",
                "DPM2": "more stable but slower",
                "Heun": "high quality but very slow"
            },
            "recommendation": "Great for quick iterations and creative exploration"
        },
        "LMS": {
            "strengths": ["smooth results", "good for portraits", "stable"],
            "weaknesses": ["can be too smooth", "loses fine details"],
            "alternatives": {
                "DPM++ 2M Karras": "better for detailed scenes",
                "Euler a": "more creative variations",
                "DPM2 a": "good balance of speed and quality"
            },
            "recommendation": "Excellent for portraits and smooth artistic styles"
        }
    },
    SettingCategory.CFG: {
        "ranges": {
            "low": (1.0, 4.0, "High creativity, low prompt adherence - good for exploration"),
            "medium": (4.0, 8.0, "Balanced creativity and adherence - general purpose"),
            "high": (8.0, 15.0, "High prompt adherence, less creative - for precise results"),
            "very_high": (15.0, 20.0, "Very strict adherence - can cause artifacts")
        }
    },
    SettingCategory.RESOLUTION: {
        "common_aspects": {
            "1:1": ["1024x1024", "Universal format", "Good for social media"],
            "16:9": ["832x1216", "Cinematic widescreen", "Great for landscapes"],
            "9:16": ["1216x832", "Portrait cinematic", "Ideal for mobile viewing"],
            "4:3": ["1024x768", "Classic aspect", "Good for traditional compositions"]
        }
    }
}


def generate_diagnostics(
    settings: Dict[str, Any],
    resources: List[Dict[str, Any]],
    level: DiagnosticLevel = DiagnosticLevel.DETAILED,
    seed: int | None = None
) -> Dict[str, Any]:
    """
    Generate comprehensive diagnostics explaining optimization choices.
    """
    if seed is not None:
        random.seed(seed)

    diagnostics = {
        "settings_explanations": {},
        "resource_analysis": _analyze_resources(resources),
        "performance_considerations": {},
        "alternative_options": {},
        "summary": "",
        "diagnostics_level": level.value
    }

    # Analyze each setting
    for setting_key, setting_value in settings.items():
        if setting_key in [cat.value for cat in SettingCategory]:
            explanation = _explain_setting(setting_key, setting_value, level)
            if explanation:
                diagnostics["settings_explanations"][setting_key] = explanation

    diagnostics["performance_considerations"] = _generate_performance_notes(settings)
    diagnostics["summary"] = _generate_summary(diagnostics, settings, resources)
    diagnostics["recommendations"] = _generate_recommendations(settings, resources)

    return diagnostics


def _explain_setting(setting_key: str, setting_value: Any, level: DiagnosticLevel) -> Dict[str, Any] | None:
    """Generate explanation for a specific setting."""
    try:
        category = SettingCategory(setting_key)
    except ValueError:
        return None

    explanation = {
        "value": setting_value,
        "reason": "",
        "alternatives": [],
        "technical_notes": ""
    }

    if category == SettingCategory.SAMPLER:
        sampler_info = DIAGNOSTIC_KNOWLEDGE[category].get(setting_value, {})
        if sampler_info:
            explanation["reason"] = f"Selected for {random.choice(sampler_info['strengths'])}"
            explanation["alternatives"] = [
                f"{alt}: {desc}" for alt, desc in sampler_info["alternatives"].items()
            ]
            explanation["technical_notes"] = sampler_info["recommendation"]

    elif category == SettingCategory.CFG:
        try:
            cfg_value = float(setting_value)
            for _, (min_val, max_val, description) in DIAGNOSTIC_KNOWLEDGE[category]["ranges"].items():
                if min_val <= cfg_value < max_val:
                    explanation["reason"] = description
                    break
        except (ValueError, TypeError):
            logger.warning(f"Invalid cfg_scale value: {setting_value}")

        if level == DiagnosticLevel.DETAILED:
            explanation["technical_notes"] = "Lower values = more creative, Higher values = more precise"
        elif level == DiagnosticLevel.EXPERT:
            explanation["technical_notes"] = "CFG controls prompt adherence vs. creativity"

    elif category == SettingCategory.RESOLUTION:
        resolution = str(setting_value)
        try:
            for aspect, (common_res, desc, note) in DIAGNOSTIC_KNOWLEDGE[category]["common_aspects"].items():
                if resolution == common_res:
                    explanation["reason"] = desc
                    explanation["technical_notes"] = note
                    break
            explanation["alternatives"] = [
                f"{res}: {desc}" for _, (res, desc, _) in DIAGNOSTIC_KNOWLEDGE[category]["common_aspects"].items()
            ]
        except Exception as e:
            logger.warning(f"Resolution analysis failed: {e}")

    elif category == SettingCategory.STEPS:
        try:
            steps = int(setting_value)
            if steps < 20:
                explanation["reason"] = "Fast generation, suitable for quick iterations"
            elif steps < 40:
                explanation["reason"] = "Balanced quality and speed, good for most purposes"
            else:
                explanation["reason"] = "High quality generation, best for final renders"
            explanation["technical_notes"] = "More steps = better quality but slower generation"
        except (ValueError, TypeError):
            logger.warning(f"Invalid steps value: {setting_value}")

    elif category == SettingCategory.DENOISE:
        try:
            denoise = float(setting_value)
            if denoise < 0.3:
                explanation["reason"] = "Minimal changes, preserves original structure"
            elif denoise < 0.6:
                explanation["reason"] = "Balanced transformation, good for most edits"
            else:
                explanation["reason"] = "Significant transformation, creative reinterpretation"
            explanation["technical_notes"] = "Controls how much the image is changed (0.0-1.0)"
        except (ValueError, TypeError):
            logger.warning(f"Invalid denoise value: {setting_value}")

    return explanation


# (rest of helper functions unchanged from your version, except with added try/except + logger in parsing)
