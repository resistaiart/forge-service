# forge/safety.py - Safety scrubbing logic for Forge

BLOCKED_CONTENT = ["minors", "underage", "non-consensual", "sexual violence"]

YOUTH_CODED_TOKENS = {
    "misty": "adult cosplayer (age 21+)",
    "jessie": "adult character (age 21+)",
    "pokemon": "cosplay creatures (fictional, age 21+)",
}

def safety_scrub(prompt: str, allow_nsfw: bool = False) -> str:
    if not isinstance(prompt, str):
        raise ValueError("Prompt must be a string")

    text = prompt.lower()

    for token in BLOCKED_CONTENT:
        if token in text:
            raise ValueError(f"Content violation: {token}")

    cleaned_prompt = prompt
    for token, replacement in YOUTH_CODED_TOKENS.items():
        cleaned_prompt = cleaned_prompt.replace(token, replacement)

    if not allow_nsfw:
        if any(word in text for word in ["nsfw", "explicit", "porn"]):
            raise ValueError("Content violation: nsfw not permitted in current mode")

    return cleaned_prompt.strip()


def build_safety(resources: dict, nsfw_allowed: bool = False) -> dict:
    return {
        "nsfw": "consensual only" if nsfw_allowed else "blocked",
        "resources": resources or {},
    }
