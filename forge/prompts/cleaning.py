import re
from typing import Dict, Optional

from forge.prompts.config import CONFIG

def clean_prompt(prompt: str) -> str:
    """
    Sanitize and deduplicate prompt content.
    Removes redundant spaces, trims punctuation artifacts,
    and eliminates duplicate words (case-insensitive).
    """
    if not isinstance(prompt, str) or not prompt.strip():
        return ""

    # Normalize spacing and punctuation
    prompt = re.sub(r"\s+", " ", prompt).strip()
    prompt = re.sub(r",\s*,", ",", prompt)
    prompt = re.sub(r"\.\s*\.", ".", prompt)

    # Deduplicate words
    seen, unique_words = set(), []
    for word in prompt.split():
        lower = word.lower()
        if lower not in seen:
            seen.add(lower)
            unique_words.append(word)

    return " ".join(unique_words)


def weight_keywords(prompt: str, custom_weights: Optional[Dict[str, float]] = None) -> str:
    """
    Apply importance weights to keywords within the prompt.
    Keywords are wrapped in ((keyword:weight)) format.
    """
    if not prompt:
        return ""

    weights = {**CONFIG["keyword_weights"], **(custom_weights or {})}
    for word in sorted(weights, key=len, reverse=True):
        pattern = re.compile(rf"\b{re.escape(word)}\b", re.IGNORECASE)
        if pattern.search(prompt):
            prompt = pattern.sub(f"(({word}:{weights[word]}))", prompt)

    return prompt
