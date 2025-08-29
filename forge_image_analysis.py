result = await run_in_threadpool(analyse_image, str(request.image_url), None, request.mode)
```

But your current `analyse_image` function:
1. Only takes 2 parameters (`image_input` and `mode`) - the `None` being passed might cause issues
2. Returns the full envelope, but `main.py` might be expecting just the result part

Let me suggest a revised version that ensures compatibility:

```python
# forge_image_analysis.py
import requests
import time
import os
import base64
from typing import Union, Dict, Any, Optional

HF_TOKEN = os.getenv("HF_TOKEN")
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}

MODELS = {
    "basic": "nlpconnect/vit-gpt2-image-captioning",
    "detailed": "Salesforce/instructblip-vicuna-7b",
}

DEFAULT_RETRY_DELAY = 30
MAX_RETRIES = 3

def query_hf(model_id: str, payload: dict) -> Any:
    """
    Send request to Hugging Face model with retry logic for cold starts.
    """
    url = f"https://api-inference.huggingface.co/models/{model_id}"
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.post(url, headers=HEADERS, json=payload, timeout=120)
            result = response.json()

            # Handle model loading errors
            if isinstance(result, dict) and "error" in result:
                error_msg = result["error"].lower()
                if "loading" in error_msg or "not found" in error_msg:
                    wait = result.get("estimated_time", DEFAULT_RETRY_DELAY)
                    print(f"[Forge] {model_id} loading, retrying in {wait}s (attempt {attempt}/{MAX_RETRIES})")
                    time.sleep(wait)
                    continue
                # Other errors should raise exception
                raise Exception(f"Hugging Face API error: {result['error']}")

            return result

        except requests.exceptions.RequestException as e:
            if attempt == MAX_RETRIES:
                raise Exception(f"Request failed after {MAX_RETRIES} attempts: {str(e)}")
            time.sleep(DEFAULT_RETRY_DELAY)
        except Exception as e:
            if attempt == MAX_RETRIES:
                raise
            time.sleep(DEFAULT_RETRY_DELAY)

    raise Exception(f"{model_id} did not respond after {MAX_RETRIES} retries")

def analyse_image(image_input: Union[str, bytes], caption: Optional[str] = None, mode: str = "basic") -> Dict[str, Any]:
    """
    Analyse image with Hugging Face models.
    
    Args:
        image_input: URL string or image bytes
        caption: Optional caption (currently unused, for future compatibility)
        mode: 'basic' or 'detailed'
    
    Returns:
        Dictionary with analysis results (compatible with main.py expectation)
    """
    if mode not in MODELS:
        raise ValueError(f"Invalid mode '{mode}'. Use 'basic' or 'detailed'.")

    model_id = MODELS[mode]

    # Handle different input types
    if isinstance(image_input, bytes):
        encoded_image = base64.b64encode(image_input).decode('utf-8')
        image_data = encoded_image
    else:
        image_data = image_input

    # Prepare payload based on mode
    if mode == "basic":
        payload = {"inputs": image_data}
    else:
        # Use caption if provided for more context-aware analysis
        question = "Describe this image in extreme detail"
        if caption:
            question = f"{question}. Context: {caption}"
        payload = {"inputs": {"image": image_data, "question": question}}

    # Query API
    result = query_hf(model_id, payload)

    # Process response
    description = ""
    if isinstance(result, list) and len(result) > 0:
        if "generated_text" in result[0]:
            description = result[0]["generated_text"].strip()
    elif isinstance(result, dict) and "generated_text" in result:
        description = result["generated_text"].strip()
    else:
        raise Exception(f"Unexpected response format from {model_id}: {result}")

    return {
        "mode": mode,
        "description": description,
        "model_used": model_id
    }

# Optional: Helper function for the envelope format if needed elsewhere
def analyse_image_with_envelope(image_input: Union[str, bytes], mode: str = "basic") -> Dict[str, Any]:
    """
    Wrapper that returns Forge-standard envelope format.
    """
    try:
        result = analyse_image(image_input, None, mode)
        return {
            "outcome": "success",
            "result": result,
            "message": f"Image analysed using {mode} mode"
        }
    except Exception as e:
        return {
            "outcome": "error",
            "result": None,
            "message": f"Image analysis failed: {str(e)}"
        }
