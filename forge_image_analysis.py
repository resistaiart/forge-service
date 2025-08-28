# forge_image_analysis.py
import requests
import os

HF_TOKEN = os.getenv("HF_TOKEN")

# Primary (higher quality) and fallback (guaranteed API availability)
PRIMARY_URL = "https://api-inference.huggingface.co/models/Salesforce/blip2-opt-2.7b"
FALLBACK_URL = "https://api-inference.huggingface.co/models/nlpconnect/vit-gpt2-image-captioning"

HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}


def query_model(api_url: str, image_url: str):
    """Send request to a Hugging Face model."""
    try:
        response = requests.post(
            api_url,
            headers=HEADERS,
            json={"inputs": image_url},
            timeout=60
        )
        return response.json()
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}


def extract_caption(result):
    """Extract caption text from HF API response."""
    if isinstance(result, list) and len(result) > 0 and "generated_text" in result[0]:
        return result[0]["generated_text"]
    return None


def analyse_image(image_url: str):
    """
    Analyse an image using Hugging Face captioning models.
    Prefer BLIP-2, fallback to ViT-GPT2.
    Returns structured descriptors for The Forge.
    """
    # Try BLIP-2 first
    result = query_model(PRIMARY_URL, image_url)
    caption = extract_caption(result)

    # If BLIP-2 failed, try ViT-GPT2
    if not caption:
        result = query_model(FALLBACK_URL, image_url)
        caption = extract_caption(result)

    if not caption:
        return {"error": f"Image analysis failed: {result}"}

    # Build Forge descriptors
    words = caption.split()
    descriptors = {
        "subject": words[1] if len(words) > 1 else caption,
        "style": "photograph, natural lighting",
        "tags": words,
        "caption": caption
    }
    return descriptors
