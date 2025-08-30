# forge/prompts/cleaning.py

import re
from typing import Dict, Optional

from forge.prompts.config import CONFIG

def clean_prompt(prompt: str) -> str:
    if not prompt or not isinstance(prompt, str):
        return ""
    prompt = re.sub(r"\s+", " ", prompt).strip()
    prompt = re.sub(r",\s*,", ",", prompt)
    prompt = re.sub(r"\.\s*\.", ".", prompt)
    seen, unique_words = set(), []
    for word in prompt.split():
        if word.lower() not in seen:
            seen.add(word.lower())
            unique_words.append(word)
    return " ".join(unique_words)


def weight_keywords(prompt: str, custom_weights: Optional[Dict] = None) -> str:
    if not prompt:
        return ""
    weights = {**CONFIG["keyword_weights"], **(custom_weights or {})}
    for word in sorted(weights.keys(), key=len, reverse=True):
        pattern = re.compile(rf"\b{re.escape(word)}\b", re.IGNORECASE)
        if pattern.search(prompt):
            prompt = pattern.sub(f"(({word}:{weights[word]}))", prompt)
    return prompt
