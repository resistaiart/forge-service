# forge_image_analysis.py

import os
import time
import base64
import requests
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format="[Forge] %(levelname)s: %(message)s")

# Hugging Face API token (stored in Railway/Env vars)
HF_TOKEN = os.getenv("HF_TOKEN")
if not HF_TOKEN:
    raise RuntimeError("[Forge] Missing Hugging Face API token (HF_TOKEN)")

HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}

# Model registry
MODELS = {
    "basic": "nlpconnect/vit-gpt2-image-captioning",
    "detailed": "Salesforce/instructblip-vicuna-7b"
}

MAX_RETRIES = 3
DEFAULT_RETRY_DELAY = 30  # seconds


def query_hf(model_id: str, payload: dict):
    """
    Sends request to Hugging Face inference API with retry logic.
    Handles model cold starts (Not Found / loading).
    """
    api_url = f"https://api-inference.huggingface.co/models/{model_id}"

    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(api_url, headers=HEADERS, json=payload, timeout=120)

            # Handle non-JSON responses
            try:
                result = response.json()
            except Exception:
                logging.error("Non-JSON response: %s", response.text[:200])
                continue

            if isinstance(result, dict) and "error" in result:
                error_message = result["error"]
                logging.warning("Attempt %d: %s", attempt + 1, error_message)

                if "loading" in error_message or "Not Found" in error_message:
                    wait_time = result.get("estimated_time", DEFAULT_RETRY_DELAY)
                    logging.info("Model loading. Retrying in %s sec...", wait_time)
                    time.sleep(wait_time)
                    continue
                else:
                    return {"outcome": "error", "message": error_message}

            return result  # Success!

        except requests.exceptions.Timeout:
            logging.error("Request timed out on attempt %d", attempt + 1)
            time.sleep(DEFAULT_RETRY_DELAY)
        except Exception as e:
            logging.error("Unexpected error: %s", str(e))
            time.sleep(DEFAULT_RETRY_DELAY)

    return {"outcome": "error", "message": "Max retries exceeded"}


def analyse_image(image_url: str = None, image_bytes: bytes = None, mode: str = "basic") -> dict:
    """
    Analyse image in either [basic] or [detailed] mode.
    Accepts either a public image URL or raw image bytes.
    """

    if not (image_url or image_bytes):
        return {"outcome": "error", "message": "Must provide image_url or image_bytes"}
    if mode not in MODELS:
        return {"outcome": "error", "message": f"Invalid mode '{mode}'"}

    model_id = MODELS[mode]

    # Prepare input
    if image_bytes:
        encoded_image = base64.b64encode(image_bytes).decode("utf-8")
        input_data = encoded_image
    else:
        input_data = image_url

    # Build payload
    if mode == "basic":
        payload = {"inputs": input_data}
    else:  # detailed mode
        payload = {
            "inputs": {
                "image": input_data,
                "question": "describe this image in extreme detail"
            }
        }

    logging.info("Sending request to %s [%s]", model_id, mode)
    result = query_hf(model_id, payload)

    # Extract description safely
    description = ""
    if isinstance(result, list) and len(result) > 0:
        description = result[0].get("generated_text", "")

    return {
        "mode": mode,
        "description": description,
        "source": model_id,
        "outcome": "success" if description else "error",
        "raw": result  # keep full response for debugging
    }
