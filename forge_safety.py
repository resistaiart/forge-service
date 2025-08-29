# forge_safety.py - Safety scrubbing logic for Forge

# 🚫 absolutely blocked content (never allowed)
BLOCKED_CONTENT = ["minors", "underage", "non-consensual", "sexual violence"]

# 🔄 replace youth-coded tokens with safe adult alternatives
YOUTH_CODED_TOKENS = {
    "misty": "adult cosplayer (age 21+)",
    "jessie": "adult character (age 21+)",
    "pokemon": "cosplay creatures (fictional, age 21+)"
}

def safety_scrub(prompt: str, allow_nsfw: bool = False) -> str:
    """
    Scrub user prompt for disallowed or unsafe content.
    
    Rules:
    - Always blocks absolute banned content (minors, underage, non-consensual, sexual violence).
    - Replaces youth-coded tokens with explicit adult-safe alternatives.
    - NSFW terms are blocked unless allow_nsfw=True (18+ mode).
    """
    if not isinstance(prompt, str):
        raise ValueError("Prompt must be a string")

    text = prompt.lower()

    # block absolute disallowed content
    for token in BLOCKED_CONTENT:
        if token in text:
            raise ValueError(f"Content violation: {token}")

    # replace youth-coded tokens
    cleaned_prompt = prompt
    for token, replacement in YOUTH_CODED_TOKENS.items():
        cleaned_prompt = cleaned_prompt.replace(token, replacement)

    # handle NSFW policy
    if not allow_nsfw:
        if "nsfw" in text or "explicit" in text or "porn" in text:
            raise ValueError("Content violation: nsfw not permitted in current mode")

    return cleaned_prompt.strip()
