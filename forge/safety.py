# forge/safety.py - Enhanced Safety scrubbing logic for Forge
import re
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

# 🚫 Absolute no-go content
BLOCKED_PATTERNS = [
    r"\b(minor|underage|child(?:ren)?|toddler|baby)\b",
    r"\b(non[-\s]?consensual|sexual\s+violence|rape|abuse)\b",
]

# 🚧 Youth-coded character replacements (safe reinterpretations)
YOUTH_CODED_TOKENS = {
    r"\bmisty\b": "adult cosplayer (age 21+)",
    r"\bjessie\b": "adult character (age 21+)",
    r"\bpokemon\b": "fictional cosplay creatures (age 21+)",
    r"\blolita\b": "adult fashion style (safe, 21+)",
}

# 🔞 Broad NSFW synonyms (only allowed if explicitly enabled)
NSFW_PATTERNS = [
    r"\bnsfw\b",
    r"\bexplicit\b",
    r"\bporn(?:ographic)?\b",
    r"\berotica?\b",
    r"\badult\s+only\b",
    r"\bsex(?:ual)?\b",
]


def safety_scrub(prompt: str, allow_nsfw: bool = False) -> str:
    """
    Scrub a prompt string for disallowed or unsafe content.

    Args:
        prompt: User input text
        allow_nsfw: Whether explicit content is allowed

    Returns:
        Cleaned prompt string

    Raises:
        ValueError if unsafe or blocked content is detected
    """
    if not isinstance(prompt, str):
        raise ValueError("Prompt must be a string")

    cleaned_prompt = prompt.strip()
    text_lower = cleaned_prompt.lower()

    # 🚫 Hard-block illegal content
    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, text_lower):
            logger.error(f"[SAFETY] Blocked content detected in prompt → '{prompt[:80]}...'")
            raise ValueError("Content violation: blocked unsafe content")

    # 🔄 Replace youth-coded tokens
    for pattern, replacement in YOUTH_CODED_TOKENS.items():
        cleaned_prompt = re.sub(pattern, replacement, cleaned_prompt, flags=re.IGNORECASE)

    # 🔞 NSFW enforcement
    if not allow_nsfw:
        for pattern in NSFW_PATTERNS:
            if re.search(pattern, text_lower):
                logger.error(f"[SAFETY] NSFW content detected but not allowed → '{prompt[:80]}...'")
                raise ValueError("Content violation: NSFW not permitted in current mode")

    return cleaned_prompt


def build_safety(resources: List[Dict[str, Any]], nsfw_allowed: bool = False) -> Dict[str, Any]:
    """
    Build a structured safety block for a package.
    """
    return {
        "status": "cleaned",
        "nsfw_policy": "consensual only" if nsfw_allowed else "blocked",
        "resources": resources or [],
    }


if __name__ == "__main__":
    # Demo safety scrubbing
    tests = [
        "Misty with Pokemon in neon city",
        "underage elf warrior",
        "nsfw cyberpunk anime scene",
        "Lolita street fashion photography"
    ]
    for t in tests:
        try:
            print("Input:", t)
            print("Output:", safety_scrub(t, allow_nsfw=False))
        except Exception as e:
            print("Blocked:", e)
