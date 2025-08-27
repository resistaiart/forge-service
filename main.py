from pathlib import Path
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
import os, json, re

# Load Forge spec from file
MASTER_SPEC = Path("forge_master_spec.md").read_text(encoding="utf-8")

API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_ID = os.getenv("MODEL_ID", "gpt-4o")  # pick a model you have access to
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

    chat = client.chat.completions.create(
        model=MODEL_ID,
        messages=[
            {"role": "system", "content": MASTER_SPEC},
            {"role": "user", "content": user_msg}
        ],
        temperature=0.2
    )

    content = chat.choices[0].message.content

    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        m = re.search(r"```json\s*(\{.*?\})\s*```", content, flags=re.S)
        if not m:
            raise HTTPException(status_code=500, detail="Model did not return JSON.")
        data = json.loads(m.group(1))

    for k in ["package_version","positive","negative","config","workflow_patch","safety","menus"]:
        if k not in data:
            raise HTTPException(status_code=500, detail=f"Missing field: {k}")

    data["package_goal"] = req.package_goal
    return data

@app.get("/")
def root():
    return {"status": "ok", "service": "forge"}
