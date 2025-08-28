# forge_image_analysis.py
import requests
import os

# Load Hugging Face API key from environment variable
HF_TOKEN = os.getenv("HF_TOKEN")
HF_API_URL = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-base"
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}

def analyse_image(image_url: str):
    """
    Analyse an image using Hugging Face CLIP Interrogator.
    Input: image URL
    Output: structured descriptors
    """
    try:
        response = requests.post(
            HF_API_URL,
            headers=HEADERS,
            json={"inputs": image_url}
        )
        result = response.json()

        # Example result structure: adjust if model returns differently
        descriptors = {
            "subject": result.get("subject", "Unknown subject"),
            "style": result.get("style", "Unknown style"),
            "tags": result.get("tags", []),
            "caption": result.get("caption", "No caption generated")
        }
        return descriptors

    except Exception as e:
        return {"error": f"Image analysis failed: {str(e)}"}
