# forge_safety.py - Safety scrubbing logic for Forge

# 🚫 absolutely blocked content (never allowed)
BLOCKED_CONTENT = ["minors", "underage", "non-consensual", "sexual violence"]

# 🔄 replace youth-coded tokens with safe adult alternatives
YOUTH_CODED_TOKENS = {
    "misty": "adult cosplayer (age 21+)",
    "jessie": "adult character (age 21+)",
    "pokemon": "cosplay creatures (fictional, age 21+)",
}

def safety_scrub(prompt: str, allow_nsfw: bool = False) -> str:
    """
    Scrub user prompt for disallowed or unsafe content.
    - Blocks absolute banned content.
    - Replaces youth-coded tokens with adult-safe alternatives.
    - Blocks NSFW unless allow_nsfw=True.
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
        if any(word in text for word in ["nsfw", "explicit", "porn"]):
            raise ValueError("Content violation: nsfw not permitted in current mode")

    return cleaned_prompt.strip()


def build_safety(resources: dict, nsfw_allowed: bool = False) -> dict:
    """
    Construct a safety metadata block for a Forge package.
    """
    return {
        "nsfw": "consensual only" if nsfw_allowed else "blocked",
        "resources": resources or {},
    }
