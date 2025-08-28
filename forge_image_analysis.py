# forge_image_analysis.py
import requests
import os
import time
import base64
import io
from PIL import Image

HF_TOKEN = os.getenv("HF_TOKEN")

# Provider registry
PROVIDERS = {
    "vit-gpt2": {
        "url": "https://api-inference.huggingface.co/models/nlpconnect/vit-gpt2-image-captioning",
        "mode": "basic",
        "payload_type": "url"  # image URL string
    },
    "instructblip": {
        "url": "https://api-inference.huggingface.co/models/Salesforce/instructblip-vicuna-7b",
        "mode": "detailed",
        "payload_type": "base64"  # base64 encoded image
    }
}

HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}


def query_model(api_url: str, payload: dict, retries: int = 3):
    """
    Query Hugging Face Inference API with retry on cold start.
    """
    for attempt in range(retries):
        response = requests.post(api_url, headers=HEADERS, json=payload, timeout=120)

        try:
            result = response.json()
        except Exception:
            return {"error": f"Non-JSON response: {response.text[:200]}"}

        # Handle HF cold start
        if "error" in result and "loading" in result["error"].lower():
            wait_time = result.get("estimated_time", 15)
            time.sleep(wait_time)
            continue  # retry after wait
        return result

    return {"error": f"Model did not respond after {retries} attempts."}


def prepare_payload(provider: str, image_url: str = None, image_file: bytes = None, prompt: str = None):
    """
    Prepare payload depending on provider requirements.
    """
    cfg = PROVIDERS[provider]

    # For vit-gpt2: pass URL
    if cfg["payload_type"] == "url":
        return {"inputs": image_url}

    # For instructblip: must send base64 image + question prompt
    if cfg["payload_type"] == "base64" and image_file:
        image = Image.open(io.BytesIO(image_file)).convert("RGB")
        buf = io.BytesIO()
        image.save(buf, format="JPEG")
        img_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        return {
            "inputs": {
                "image": img_b64,
                "question": prompt or "Describe this image in extreme detail."
            }
        }

    return {"error": "Invalid payload config or missing image file."}


def extract_caption(result):
    """
    Extract generated text from HF response.
    """
    if isinstance(result, list) and len(result) > 0 and "generated_text" in result[0]:
        return result[0]["generated_text"]
    return None


def analyse_image(provider: str, image_url: str = None, image_file: bytes = None, prompt: str = None):
    """
    Analyse an image with the chosen provider and return Forge descriptors.
    """
    if provider not in PROVIDERS:
        return {"error": f"Unknown provider: {provider}"}

    cfg = PROVIDERS[provider]
    payload = prepare_payload(provider, image_url, image_file, prompt)
    if "error" in payload:
        return payload

    result = query_model(cfg["url"], payload)
    caption = extract_caption(result)
    if not caption:
        return {"error": f"Image analysis failed: {result}"}

    # Forge descriptor schema
    words = caption.split()
    descriptors = {
        "provider": provider,
        "mode": cfg["mode"],
        "subject": words[1] if len(words) > 1 else caption,
        "style": "photograph, natural lighting" if provider == "vit-gpt2" else "detailed, descriptive analysis",
        "tags": words,
        "caption": caption
    }
    return descriptors
