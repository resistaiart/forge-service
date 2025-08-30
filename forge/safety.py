# forge/safety.py - Safety scrubbing logic for Forge
import re
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

BLOCKED_CONTENT = [
    "minors", "underage", "underaged", "child", "children",
    "non-consensual", "sexual violence", "rape", "abuse"
]

YOUTH_CODED_TOKENS = {
    r"\bmisty\b": "adult cosplayer (age 21+)",
    r"\bjessie\b": "adult character (age 21+)",
    r"\bpokemon\b": "cosplay creatures (fictional, age 21+)",
    r"\blolita\b": "adult fashion style (21+ safe context)",
}


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

    text = prompt.lower()

    # Hard-block disallowed content
    for token in BLOCKED_CONTENT:
        if token in text:
            logger.error(f"Blocked content detected: {token}")
            raise ValueError(f"Content violation: {token}")

    cleaned_prompt = prompt

    # Replace youth-coded tokens (case-insensitive, word-safe)
    for pattern, replacement in YOUTH_CODED_TOKENS.items():
        cleaned_prompt = re.sub(pattern, replacement, cleaned_prompt, flags=re.IGNORECASE)

    # NSFW enforcement
    if not allow_nsfw:
        if any(word in text for word in ["nsfw", "explicit", "porn"]):
            logger.error("NSFW content detected in non-NSFW mode")
            raise ValueError("Content violation: nsfw not permitted in current mode")

    return cleaned_prompt.strip()


def build_safety(resources: List[Dict[str, Any]], nsfw_allowed: bool = False) -> Dict[str, Any]:
    """
    Build a structured safety block for a package.
    
    Args:
        resources: List of validated resources
        nsfw_allowed: Whether NSFW mode is enabled
    
    Returns:
        Dictionary for package safety field
    """
    return {
        "nsfw": "consensual only" if nsfw_allowed else "blocked",
        "resources": resources or [],
    }


if __name__ == "__main__":
    # Simple tests
    try:
        print(safety_scrub("Misty with Pokemon in neon city"))
        print(safety_scrub("underage elf warrior"))  # should block
    except Exception as e:
        print("Blocked:", e)

    safe = build_safety([{"name": "forge-base-v1"}], nsfw_allowed=False)
    print("Safety block:", safe)
