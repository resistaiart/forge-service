# forge_image_analysis.py
import requests
import time
import os

HF_TOKEN = os.getenv("HF_TOKEN")
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}

MODELS = {
    "basic": "nlpconnect/vit-gpt2-image-captioning",        # fast, concise captions
    "detailed": "Salesforce/instructblip-vicuna-7b"         # slower, detailed analysis
}

DEFAULT_RETRY_DELAY = 30
MAX_RETRIES = 3


def query_hf(model_id: str, payload: dict):
    """
    Send request to Hugging Face model with retry logic for cold starts.
    """
    url = f"https://api-inference.huggingface.co/models/{model_id}"
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.post(url, headers=HEADERS, json=payload, timeout=120)
            result = response.json()

            # Error handling: cold start or model not ready
            if isinstance(result, dict) and "error" in result:
                error_message = result["error"]
                if "loading" in error_message or "Not Found" in error_message:
                    wait = result.get("estimated_time", DEFAULT_RETRY_DELAY)
                    print(f"[Forge] {model_id} cold start (attempt {attempt}/{MAX_RETRIES}), retrying in {wait}s")
                    time.sleep(wait)
                    continue
                # Other error → fail fast
                raise Exception(f"Hugging Face API error: {error_message}")

            # Successful result
            return result

        except Exception as e:
            if attempt == MAX_RETRIES:
                raise Exception(f"[Forge] Failed after {MAX_RETRIES} attempts: {str(e)}")
            time.sleep(DEFAULT_RETRY_DELAY)

    raise Exception(f"[Forge] {model_id} did not respond after retries")


def analyse_image(image_url: str, mode: str = "basic"):
    """
    Analyse image with either basic or detailed mode.
    - basic: generates a short caption
    - detailed: generates a more descriptive analysis
    """
    if mode not in MODELS:
        return {"error": f"Invalid mode '{mode}'. Use 'basic' or 'detailed'."}

    model_id = MODELS[mode]

    # Basic model: just needs inputs
    if mode == "basic":
        payload = {"inputs": image_url}
        result = query_hf(model_id, payload)
        return {"mode": mode, "description": result[0].get("generated_text", "")}

    # Detailed model: instruction-following
    if mode == "detailed":
        payload = {"inputs": {"image": image_url, "question": "Describe this image in extreme detail"}}
        result = query_hf(model_id, payload)
        return {"mode": mode, "description": result[0].get("generated_text", "")}
