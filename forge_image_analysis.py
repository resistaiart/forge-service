# forge_image_analysis.py
import requests
import os

HF_TOKEN = os.getenv("HF_TOKEN")
HF_API_URL = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-base"
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
        result = response.json()

        if isinstance(result, list) and "generated_text" in result[0]:
            caption = result[0]["generated_text"]
        else:
            return {"error": f"Unexpected response: {result}"}

        # Very simple heuristic split
        descriptors = {
            "subject": caption.split()[1] if len(caption.split()) > 1 else caption,
            "style": "photograph, natural lighting",
            "tags": caption.split(),
            "caption": caption
        }
        return descriptors

    except Exception as e:
        return {"error": f"Image analysis failed: {str(e)}"}
