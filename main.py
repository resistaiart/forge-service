from pathlib import Path
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
import os, json, re

# Load Forge spec from file
MASTER_SPEC = Path("forge_master_spec.md").read_text(encoding="utf-8")

API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_ID = os.getenv("MODEL_ID", "gpt-4o")  # default to gpt-4o
if not API_KEY:
    raise RuntimeError("OPENAI_API_KEY is not set")

client = OpenAI(api_key=API_KEY)

app = FastAPI(title="Forge Service", version="1.0.0")


class OptimiseRequest(BaseModel):
    package_goal: str  # "t2i" | "i2i" | "t2v" | "i2v"
    prompt: str
    resources: Optional[Dict[str, Any]] = None


@app.post("/optimise")
def optimise(req: OptimiseRequest):
    user_msg = (
        "Request: prompt optimisation\n"
        f"Package goal: {req.package_goal}\n"
        f"Prompt: {req.prompt}\n"
        f"Resources: {req.resources or {}}\n"
        "Respond as strict JSON with fields:"
        "{\"package_version\":\"v1.0\",\"positive\":\"\",\"negative\":\"\","
        "\"config\":{},\"workflow_patch\":{},\"safety\":{},"
        "\"menus\":[\"variants\",\"prompt\",\"negatives\",\"config\",\"workflow\",\"version\",\"rationale\",\"discard\",\"help\"]}"
    )

    try:
        chat = client.chat.completions.create(
            model=MODEL_ID,
            messages=[
                {"role": "system", "content": MASTER_SPEC},
                {"role": "user", "content": user_msg}
            ],
            temperature=0.2
        )
    except Exception as e:
        # Surface OpenAI errors directly
        raise HTTPException(status_code=502, detail=f"OpenAI error: {e}")

    content = chat.choices[0].message.content

    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        m = re.search(r"```json\s*(\{.*?\})\s*```", content, flags=re.S)
        if not m:
            raise HTTPException(status_code=500, detail="Model did not return JSON.")
        data = json.loads(m.group(1))

    for k in ["package_version", "positive", "negative", "config",
              "workflow_patch", "safety", "menus"]:
        if k not in data:
            raise HTTPException(status_code=500, detail=f"Missing field: {k}")

    data["package_goal"] = req.package_goal
    return data


@app.get("/")
def root():
    return {"status": "ok", "service": "forge"}


# --- Diagnostic routes ---

@app.get("/env-check")
def env_check():
    """Check if API key + model are loaded correctly"""
    k = os.getenv("OPENAI_API_KEY", "")
    return {
        "has_key": bool(k),
        "prefix": (k[:3] if k else None),
        "len": (len(k) if k else 0),
        "model_id": MODEL_ID,
    }


@app.get("/health/openai")
def health_openai():
    """Lightweight OpenAI check"""
    try:
        _ = client.models.list()
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}
