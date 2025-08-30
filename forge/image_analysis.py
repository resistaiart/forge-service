# forge/image_analysis.py
import requests
import time
import os
import base64
import logging
from typing import Union, Dict, Any, Optional

logger = logging.getLogger(__name__)

# Config
HF_TOKEN = os.getenv("HF_TOKEN")
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"} if HF_TOKEN else {}

MODELS = {
    "basic": "Salesforce/blip-image-captioning-base",
    "detailed": "Salesforce/instructblip-vicuna-7b",
    "tags": "Salesforce/blip-image-captioning-base",  # tags use BLIP base under the hood
}

DEFAULT_RETRY_DELAY = 30
MAX_RETRIES = 3

STOPWORDS = {"the", "and", "with", "this", "that", "for", "from", "into", "onto", "very"}


def query_hf(model_id: str, payload: dict) -> Any:
    """Send request to Hugging Face model with retry logic for cold starts."""
    if not HF_TOKEN:
        raise RuntimeError("HF_TOKEN not configured. Set environment variable.")

    url = f"https://api-inference.huggingface.co/models/{model_id}"

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.post(url, headers=HEADERS, json=payload, timeout=120)
            response.raise_for_status()
            result = response.json()

            if isinstance(result, dict) and "error" in result:
                error_msg = result["error"].lower()
                if "loading" in error_msg or "not found" in error_msg:
                    wait = result.get("estimated_time", DEFAULT_RETRY_DELAY)
                    logger.info(f"{model_id} loading... retry in {wait}s (attempt {attempt}/{MAX_RETRIES})")
                    time.sleep(wait)
                    continue
                raise RuntimeError(f"Hugging Face API error: {result['error']}")

            return result

        except requests.exceptions.RequestException as e:
            logger.warning(f"Request failed (attempt {attempt}/{MAX_RETRIES}): {e}")
            if attempt == MAX_RETRIES:
                raise
            time.sleep(DEFAULT_RETRY_DELAY)
        except Exception as e:
            logger.error(f"Unexpected error (attempt {attempt}/{MAX_RETRIES}): {e}")
            if attempt == MAX_RETRIES:
                raise
            time.sleep(DEFAULT_RETRY_DELAY)

    raise RuntimeError(f"{model_id} did not respond after {MAX_RETRIES} retries")


def _clean_tags(description: str) -> list[str]:
    """Split a caption into cleaned keyword tags."""
    words = [w.strip(".,").lower() for w in description.split()]
    tags = [w for w in words if len(w) > 2 and w not in STOPWORDS]
    return list(dict.fromkeys(tags))  # dedupe while preserving order


def analyse_image(
    image_input: Union[str, bytes],
    caption: Optional[str] = None,
    mode: str = "basic"
) -> Dict[str, Any]:
    """Analyse image with Hugging Face models."""
    if mode not in MODELS:
        raise ValueError(f"Invalid mode '{mode}'. Use 'basic', 'detailed', or 'tags'.")

    model_id = MODELS[mode]

    # Encode input
    if isinstance(image_input, bytes):
        image_data = base64.b64encode(image_input).decode("utf-8")
    else:
        image_data = image_input

    # Build payload
    if mode in {"basic", "tags"}:
        payload = {"inputs": image_data}
    else:
        question = (
            "Describe this image in extreme detail. Include objects, colors, "
            "composition, style, mood, and any text visible."
        )
        if caption:
            question += f" Context: {caption}"
        payload = {"inputs": {"image": image_data, "question": question}}

    # Query model
    result = query_hf(model_id, payload)

    # Extract description
    description = ""
    if isinstance(result, list) and result and "generated_text" in result[0]:
        description = result[0]["generated_text"].strip()
    elif isinstance(result, dict) and "generated_text" in result:
        description = result["generated_text"].strip()
    else:
        raise RuntimeError(f"Unexpected response format from {model_id}: {result}")

    if mode == "tags":
        return {
            "mode": mode,
            "tags": _clean_tags(description),
            "raw_caption": description,
            "model_used": model_id,
        }

    return {"mode": mode, "description": description, "model_used": model_id}


def analyse_image_with_envelope(image_input: Union[str, bytes], mode: str = "basic") -> Dict[str, Any]:
    """Return Forge-standard envelope format."""
    try:
        result = analyse_image(image_input, None, mode)
        return {"outcome": "success", "result": result, "message": f"Image analysed using {mode} mode"}
    except Exception as e:
        logger.exception("Image analysis failed")
        return {"outcome": "error", "result": None, "message": f"Image analysis failed: {str(e)}"}


def analyse_sealed(request: dict) -> Dict[str, Any]:
    """Sealed entrypoint for API route /v2/analyse."""
    image_url = request.get("image_url")
    mode = request.get("mode", "basic")

    if not image_url:
        return {"outcome": "error", "result": None, "message": "image_url is required"}

    return analyse_image_with_envelope(image_url, mode)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    test_url = "https://huggingface.co/datasets/hf-internal-testing/example-images/resolve/main/cat.png"

    for mode in ["basic", "detailed", "tags"]:
        try:
            logger.info(f"Testing {mode} analysis...")
            result = analyse_image(test_url, mode=mode)
            logger.info(f"{mode.capitalize()} result: {result}")
        except Exception as e:
            logger.error(f"Error in {mode} mode: {e}")
