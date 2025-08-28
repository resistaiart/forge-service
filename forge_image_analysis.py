# forge_image_analysis.py
import os
import requests

HF_TOKEN = os.getenv("HF_TOKEN")
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}

MODELS = {
    "basic": "nlpconnect/vit-gpt2-image-captioning",
    "detailed": "Salesforce/instructblip-vicuna-7b"
    # style/subject could be mapped to future models or pipelines
}

def analyse_image(image_url: str, mode: str = "basic"):
    """
    Analyse an image using Hugging Face inference API.
    Mode determines which model/tool is used.
    """
    model_id = MODELS.get(mode)
    if not model_id:
        return {"error": f"Unsupported mode: {mode}"}

    api_url = f"https://api-inference.huggingface.co/models/{model_id}"

    payload = {"inputs": image_url}
    try:
        response = requests.post(api_url, headers=HEADERS, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()

        if isinstance(data, list) and "generated_text" in data[0]:
            return {mode: data[0]["generated_text"]}

        return {mode: str(data)}

    except requests.exceptions.RequestException as e:
        return {"error": f"Request failed: {e}"}
    except Exception as e:
        return {"error": f"Unexpected error: {e}"}
