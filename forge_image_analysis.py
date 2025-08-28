# forge_image_analysis.py
import requests
import time
import os
import base64
from typing import Union, Dict, Any

# ---- Config ----
HF_TOKEN = os.getenv("HF_TOKEN")
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}

MODELS = {
    "basic": "nlpconnect/vit-gpt2-image-captioning",
    "detailed": "Salesforce/instructblip-vicuna-7b"
}

DEFAULT_RETRY_DELAY = 30
MAX_RETRIES = 3
MIN_CALL_INTERVAL = 1.0

DETAILED_PROMPTS = {
    "general": "Describe this image in extreme detail. Include objects, colors, composition, style, mood, and any visible text",
    "technical": "Provide a technical description: composition, lighting, color palette, artistic style, quality",
    "artistic": "Analyze as an art critic: style, technique, emotional impact, influences",
    "accessibility": "Create detailed alt text for accessibility purposes"
}

LAST_CALL_TIME = 0

# ---- Rate limiting ----
def rate_limited_query():
    global LAST_CALL_TIME
    now = time.time()
    elapsed = now - LAST_CALL_TIME
    if elapsed < MIN_CALL_INTERVAL:
        time.sleep(MIN_CALL_INTERVAL - elapsed)
    LAST_CALL_TIME = time.time()

# ---- Response handling ----
def process_hf_response(result: Any, model_id: str) -> str:
    """Validate and extract text from HF response."""
    if isinstance(result, list) and len(result) > 0:
        if "generated_text" in result[0]:
            return result[0]["generated_text"].strip()
    elif isinstance(result, dict) and "generated_text" in result:
        return result["generated_text"].strip()
    raise Exception(f"Unexpected response format from {model_id}: {result}")

# ---- HF Query ----
def query_hf(model_id: str, payload: dict) -> Any:
    """Send request to HF model with retries + cold start handling."""
    url = f"https://api-inference.huggingface.co/models/{model_id}"

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            rate_limited_query()
            resp = requests.post(url, headers=HEADERS, json=payload, timeout=120)
            resp.raise_for_status()
            result = resp.json()

            # Handle API error messages
            if isinstance(result, dict) and "error" in result:
                err = result["error"].lower()
                if "loading" in err or "not found" in err:
                    wait = result.get("estimated_time", DEFAULT_RETRY_DELAY)
                    print(f"[Forge] {model_id} cold start (attempt {attempt}/{MAX_RETRIES}), retry {wait}s")
                    time.sleep(wait); continue
                if "rate limit" in err:
                    print(f"[Forge] rate limited, retry {DEFAULT_RETRY_DELAY}s")
                    time.sleep(DEFAULT_RETRY_DELAY); continue

            return result

        except requests.exceptions.Timeout:
            print(f"[Forge] timeout (attempt {attempt}/{MAX_RETRIES})")
            if attempt == MAX_RETRIES: raise Exception("Timeout after retries")
            time.sleep(DEFAULT_RETRY_DELAY)

        except requests.exceptions.HTTPError as e:
            if resp.status_code == 503:  # service unavailable
                print(f"[Forge] service unavailable (attempt {attempt}/{MAX_RETRIES})")
                time.sleep(DEFAULT_RETRY_DELAY); continue
            raise

        except Exception as e:
            if attempt == MAX_RETRIES:
                raise Exception(f"Failed after {MAX_RETRIES} retries: {str(e)}")
            time.sleep(DEFAULT_RETRY_DELAY)

    raise Exception(f"{model_id} no response after retries")

# ---- Main API ----
def analyse_image(image_input: Union[str, bytes], mode: str = "basic", style: str = "general") -> Dict[str, str]:
    """
    Analyse image
    - image_input: URL or raw bytes
    - mode: [basic] (fast caption) | [detailed] (rich description)
    - style: only for detailed (general, technical, artistic, accessibility)
    """
    if mode not in MODELS:
        return {"error": f"Invalid mode '{mode}' use 'basic' or 'detailed'"}

    model_id = MODELS[mode]

    # Input as base64 (for bytes) or pass URL
    if isinstance(image_input, bytes):
        image_data = base64.b64encode(image_input).decode("utf-8")
    else:
        image_data = image_input

    # Build payload
    if mode == "basic":
        payload = {"inputs": image_data}
    else:
        q = DETAILED_PROMPTS.get(style, DETAILED_PROMPTS["general"])
        payload = {"inputs": {"image": image_data, "question": q}}

    # Query HF + process
    result = query_hf(model_id, payload)
    desc = process_hf_response(result, model_id)

    return {
        "mode": mode,
        "style": style if mode == "detailed" else "n/a",
        "description": desc,
        "model_used": model_id
    }
