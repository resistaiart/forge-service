# forge_image_analysis.py
import requests
import os

HF_TOKEN = os.getenv("HF_TOKEN")

# Guaranteed free-tier model
HF_API_URL = "https://api-inference.huggingface.co/models/nlpconnect/vit-gpt2-image-captioning"
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}

def analyse_image(image_url: str):
    """
    Analyse an image using Hugging Face ViT-GPT2 captioning model.
    Returns structured descriptors for The Forge.
    """
    try:
        response = requests.post(
            HF_API_URL,
            headers=HEADERS,
            json={"inputs": image_url},
            timeout=60
        )

        try:
            result = response.json()
        except Exception:
            return {"error": f"Non-JSON response: {response.text[:200]}"}

        if isinstance(result, list) and len(result) > 0 and "generated_text" in result[0]:
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
