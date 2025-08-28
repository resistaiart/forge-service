# forge_image_analysis.py
import requests
import os

HF_TOKEN = os.getenv("HF_TOKEN")

# Preferred + fallback models
PRIMARY_URL = "https://api-inference.huggingface.co/models/Salesforce/blip2-opt-2.7b"
FALLBACK_URL = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-large"

HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}


def query_model(api_url: str, image_url: str):
    """Send request to Hugging Face model."""
    response = requests.post(
        api_url,
        headers=HEADERS,
        json={"inputs": image_url}
    )
    try:
        return response.json()
    except Exception:
        return {"error": f"Non-JSON response: {response.text[:200]}"}


def analyse_image(image_url: str):
    """
    Analyse an image using Hugging Face captioning models.
    Prefer BLIP-2, fallback to BLIP Large.
    """
    # Try BLIP-2
    result = query_model(PRIMARY_URL, image_url)
    if isinstance(result, list) and "generated_text" in result[0]:
        caption = result[0]["generated_text"]
    else:
        # Fallback to BLIP Large
        result = query_model(FALLBACK_URL, image_url)
        if isinstance(result, list) and "generated_text" in result[0]:
            caption = result[0]["generated_text"]
        else:
            return {"error": f"Image analysis failed: {result}"}

    # Build descriptors
    words = caption.split()
    descriptors = {
        "subject": words[1] if len(words) > 1 else caption,
        "style": "photograph, natural lighting",
        "tags": words,
        "caption": caption
    }
    return descriptors
