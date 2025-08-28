# forge_image_analysis.py
import requests
import time
import os
import base64

HF_TOKEN = os.getenv("HF_TOKEN")
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}

MODELS = {
    "basic": "nlpconnect/vit-gpt2-image-captioning",
    "detailed": "Salesforce/instructblip-vicuna-7b"
}

DEFAULT_RETRY_DELAY = 30
MAX_RETRIES = 3

def query_hf(model_id: str, payload: dict):
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
                    time.sleep(wait)
                    continue
            return result

        except Exception as e:
            if attempt == MAX_RETRIES:
                raise
            time.sleep(DEFAULT_RETRY_DELAY)

    raise Exception(f"{model_id} failed after {MAX_RETRIES} attempts")

def analyse_image(image_url: str, mode: str = "basic"):
    """
    Analyse image with Hugging Face model.
    Always wrapped in {outcome, result, message}.
    """
    try:
        if mode not in MODELS:
            return {
                "outcome": "error",
                "result": None,
                "message": f"invalid mode {mode} use basic or detailed"
            }

        model_id = MODELS[mode]

        if mode == "basic":
            payload = {"inputs": image_url}
        else:
            payload = {
                "inputs": {
                    "image": image_url,
                    "question": "describe this image in extreme detail"
                }
            }

        result = query_hf(model_id, payload)

        description = (
            result[0].get("generated_text", "")
            if isinstance(result, list) and len(result) > 0
            else str(result)
        )

        return {
            "outcome": "success",
            "result": {
                "mode": mode,
                "description": description,
                "model_used": model_id,
            },
            "message": f"analysis complete in {mode} mode",
        }

    except Exception as e:
        return {
            "outcome": "error",
            "result": None,
            "message": f"analysis failed {str(e)}",
        }
