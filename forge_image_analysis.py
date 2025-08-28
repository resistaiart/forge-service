# forge_image_analysis.py
import requests, time, os, base64
from typing import Union, Dict, Any

HF_TOKEN = os.getenv("HF_TOKEN")
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}

MODELS = {
    "basic": "nlpconnect/vit-gpt2-image-captioning",
    "detailed": "Salesforce/instructblip-vicuna-7b",
}

DEFAULT_RETRY_DELAY = 30
MAX_RETRIES = 3

def query_hf(model_id: str, payload: dict) -> Any:
    url = f"https://api-inference.huggingface.co/models/{model_id}"
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.post(url, headers=HEADERS, json=payload, timeout=120)
            result = response.json()
            if isinstance(result, dict) and "error" in result:
                if "loading" in result["error"].lower() or "not found" in result["error"].lower():
                    wait = result.get("estimated_time", DEFAULT_RETRY_DELAY)
                    time.sleep(wait)
                    continue
            return result
        except Exception:
            if attempt == MAX_RETRIES:
                raise
            time.sleep(DEFAULT_RETRY_DELAY)
    raise Exception("HF model unresponsive")

def analyse_image(image_input: Union[str, bytes], mode: str = "basic") -> Dict[str, Any]:
    """
    Analyse image with Hugging Face models
    Returns Forge-standard envelope: {outcome, result, message}
    """
    try:
        if mode not in MODELS:
            return {"outcome": "error", "message": f"invalid mode {mode}", "result": None}

        model_id = MODELS[mode]

        if isinstance(image_input, bytes):
            image_data = base64.b64encode(image_input).decode("utf-8")
        else:
            image_data = image_input

        if mode == "basic":
            payload = {"inputs": image_data}
        else:
            payload = {"inputs": {"image": image_data, "question": "Describe this image in detail"}}

        result = query_hf(model_id, payload)

        description = ""
        if isinstance(result, list) and len(result) > 0 and "generated_text" in result[0]:
            description = result[0]["generated_text"].strip()
        elif isinstance(result, dict) and "generated_text" in result:
            description = result["generated_text"].strip()
        else:
            return {"outcome": "error", "message": f"unexpected response {result}", "result": None}

        return {
            "outcome": "success",
            "result": {"mode": mode, "description": description, "model_used": model_id},
            "message": "analysed",
        }
    except Exception as e:
        return {"outcome": "error", "message": f"analysis failed: {str(e)}", "result": None}
