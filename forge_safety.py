# forge_safety.py - Just the safety scrubbing logic
BLOCKED_CONTENT = ["minors", "underage", "non-consensual", "sexual violence"]
YOUTH_CODED_TOKENS = {"misty": "adult cosplayer", "jessie": "adult character"}

def safety_scrub(prompt: str) -> str:
    # ... implementation from earlier
    return cleaned_prompt
