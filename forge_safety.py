# forge_safety.py - Safety scrubbing logic for Forge

BLOCKED_CONTENT = ["minors", "underage", "non-consensual", "sexual violence"]

YOUTH_CODED_TOKENS = {
    "misty": "adult cosplayer (age 21+)",
    "jessie": "adult character (age 21+)",
    "pokemon": "cosplay creatures (fictional, age 21+)"
}

def safety_scrub(prompt: str, allow_nsfw: bool = False) -> str:
    """
    Scrub user prompt for disallowed or unsafe content.
    - Blocks content with disallowed terms.
    - Replaces youth-coded tokens with safe alternatives.
    - Allows NSFW if explicitly enabled (18+ assumption).
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
