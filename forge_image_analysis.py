# forge_image_analysis.py
import requests
import time
import os
import base64
import logging
from typing import Union, Dict, Any, Optional

# Set up logging
logger = logging.getLogger(__name__)

# Configuration
HF_TOKEN = os.getenv("HF_TOKEN")
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"} if HF_TOKEN else {}

MODELS = {
    "basic": "Salesforce/blip-image-captioning-base",
    "detailed": "Salesforce/instructblip-vicuna-7b",
    # 🔥 new tags mode uses blip-base under the hood
    "tags": "Salesforce/blip-image-captioning-base",
}

DEFAULT_RETRY_DELAY = 30
MAX_RETRIES = 3

def query_hf(model_id: str, payload: dict) -> Any:
    """
    Send request to Hugging Face model with retry logic for cold starts.
    """
    if not HF_TOKEN:
        raise Exception("Hugging Face token not configured. Set HF_TOKEN environment variable.")
    
    url = f"https://api-inference.huggingface.co/models/{model_id}"
    
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.post(url, headers=HEADERS, json=payload, timeout=120)
            response.raise_for_status()
            result = response.json()
            
            # Handle model loading errors
            if isinstance(result, dict) and "error" in result:
                error_msg = result["error"].lower()
                if "loading" in error_msg or "not found" in error_msg:
                    wait = result.get("estimated_time", DEFAULT_RETRY_DELAY)
                    logger.info(f"{model_id} loading, retrying in {wait}s (attempt {attempt}/{MAX_RETRIES})")
                    time.sleep(wait)
                    continue
                # Other errors should raise exception
                raise Exception(f"Hugging Face API error: {result['error']}")
            
            return result

        except requests.exceptions.RequestException as e:
            logger.warning(f"Request failed (attempt {attempt}/{MAX_RETRIES}): {e}")
            if attempt == MAX_RETRIES:
                raise Exception(f"Request failed after {MAX_RETRIES} attempts: {str(e)}")
            time.sleep(DEFAULT_RETRY_DELAY)
        except Exception as e:
            logger.error(f"Unexpected error (attempt {attempt}/{MAX_RETRIES}): {e}")
            if attempt == MAX_RETRIES:
                raise
            time.sleep(DEFAULT_RETRY_DELAY)

    raise Exception(f"{model_id} did not respond after {MAX_RETRIES} retries")

def analyse_image(image_input: Union[str, bytes], caption: Optional[str] = None, mode: str = "basic") -> Dict[str, Any]:
    """
    Analyse image with Hugging Face models.
    
    Args:
        image_input: URL string or image bytes
        caption: Optional caption for context
        mode: 'basic', 'detailed', or 'tags'
    
    Returns:
        Dictionary with analysis results
    """
    try:
        if mode not in MODELS:
            raise ValueError(f"Invalid mode '{mode}'. Use 'basic', 'detailed', or 'tags'.")

        model_id = MODELS[mode]

        # Handle different input types
        if isinstance(image_input, bytes):
            encoded_image = base64.b64encode(image_input).decode('utf-8')
            image_data = encoded_image
        else:
            image_data = image_input

        # Prepare payload
        if mode == "basic" or mode == "tags":
            payload = {"inputs": image_data}
        else:
            question = "Describe this image in extreme detail. Include objects, colors, composition, style, mood, and any text visible."
            if caption:
                question = f"{question} Context: {caption}"
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

        # If tags mode, split description into keyword tags
        if mode == "tags":
            words = [w.strip(".,").lower() for w in description.split()]
            tags = list(dict.fromkeys([w for w in words if len(w) > 2]))  # dedup, no tiny words
            return {
                "mode": mode,
                "tags": tags,
                "raw_caption": description,
                "model_used": model_id
            }

        return {
            "mode": mode,
            "description": description,
            "model_used": model_id
        }
        
    except Exception as e:
        logger.error(f"Image analysis failed: {e}")
        raise Exception(f"Image analysis failed: {str(e)}")

# Helper function for standard response format
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

# 🔥 NEW: sealed API entrypoint for main.py
def analyse_sealed(request: dict) -> Dict[str, Any]:
    """
    Sealed entrypoint for API route /v2/analyse.
    """
    image_url = request.get("image_url")
    mode = request.get("mode", "basic")

    if not image_url:
        return {
            "outcome": "error",
            "result": None,
            "message": "image_url is required"
        }

    return analyse_image_with_envelope(image_url, mode)

# Example usage and testing
if __name__ == "__main__":
    # Configure logging for testing
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    
    test_url = "https://huggingface.co/datasets/hf-internal-testing/example-images/resolve/main/cat.png"
    
    try:
        print("Testing basic analysis...")
        result_basic = analyse_image(test_url, mode="basic")
        print(f"Basic result: {result_basic['description']}")
        
        print("\nTesting detailed analysis...")
        result_detailed = analyse_image(test_url, mode="detailed")
        print(f"Detailed result: {result_detailed['description']}")
        
        print("\nTesting tags analysis...")
        result_tags = analyse_image(test_url, mode="tags")
        print(f"Tags result: {result_tags['tags']}")
        
    except Exception as e:
        print(f"Error: {e}")
