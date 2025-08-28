# forge_image_analysis.py
import requests
import os

HF_TOKEN = os.getenv("HF_TOKEN")
HF_API_URL = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-large"
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}

def analyse_image(image_url: str):
    """
    Analyse an image using Hugging Face BLIP model.
    Returns structured descriptors for The Forge.
    """
    try:
        response = requests.post(
            HF_API_URL,
            headers=HEADERS,
            json={"inputs": image_url}
        )

        # Debug: show raw response if it fails
        try:
            result = response.json()
        except Exception:
            return {"error": f"Non-JSON response: {response.text[:200]}"}

        if isinstance(result, list) and "generated_text" in result[0]:
            caption = result[0]["generated_text"]
        else:
            return {"error": f"Unexpected response format: {result}"}

        # Build Forge descriptors
        words = caption.split()
        descriptors = {
            "subject": words[1] if len(words) > 1 else caption,
            "style": "photograph, natural lighting",
            "tags": words,
            "caption": caption
        }
        return descriptors

    except Exception as e:
        return {"error": f"Image analysis failed: {str(e)}"}
