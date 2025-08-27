import os
from fastapi import FastAPI, HTTPException, Security
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from fastapi.security.api_key import APIKeyHeader

# ---------------------------------------------------------
# API Key (Railway or fallback for local dev)
# ---------------------------------------------------------
API_KEY = os.getenv("API_KEY", "supersecret")
api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)

app = FastAPI(title="Forge API", version="2.1.0")

# ---------------------------------------------------------
# Models
# ---------------------------------------------------------
class OptimiseRequest(BaseModel):
    package_goal: str = Field(..., description="t2i, i2i, t2v, i2v")
    prompt: str = Field(..., description="Raw user prompt text")
    resources: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ForgePackage(BaseModel):
    package_version: str
    positive: str
    negative: str
    config: Dict[str, Any]
    workflow_patch: Dict[str, Any]
    safety: Dict[str, Any]
    resources: Dict[str, Any]
    menus: List[str]
    menus_help: Dict[str, Any]
    prompt_suggestions: List[str]
    workflow_suggestions: List[str]
    package_goal: str

# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------
def apply_safety(prompt: str) -> (str, Dict[str, Any]):
    """Safety filter: enforce NSFW rules, auto-clean IP/minor-coded tokens."""
    safety_info = {"nsfw": "consensual only", "blocked": []}
    cleaned_prompt = prompt

    banned_tokens = ["Misty", "Jessie", "Pokemon"]
    for token in banned_tokens:
        if token.lower() in cleaned_prompt.lower():
            safety_info["blocked"].append(token)
            cleaned_prompt = cleaned_prompt.replace(
                token, "adult cosplayer lookalike (age 21+)"
            )
    return cleaned_prompt, safety_info


def build_config(overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    config = {
        "sampler": "DPM++ 2M Karras",
        "steps": 30,
        "cfg": 7.0,
        "resolution": "1024x768",
        "seed": 123456789,
    }
    if overrides:
        config.update(overrides)
    return config


def build_workflow_patch(config: Dict[str, Any]) -> Dict[str, Any]:
    width, height = map(int, config["resolution"].split("x"))
    return {
        "nodes": [
            {
                "op": "set",
                "node": "KSampler",
                "params": {
                    "steps": config["steps"],
                    "cfg": config["cfg"],
                    "seed": config["seed"],
                },
            },
            {
                "op": "set",
                "node": "EmptyLatentImage",
                "params": {"width": width, "height": height},
            },
        ]
    }


def build_menus() -> List[str]:
    return ["variants", "prompt", "config", "workflow", "version", "rationale", "discard", "help"]


def build_menus_help() -> Dict[str, Any]:
    return {
        "global": {
            "variants": "Generate alternative package versions.",
            "prompt": "View and refine positive/negative prompts.",
            "config": "Adjust generation parameters (sampler, steps, CFG, resolution, seed, LoRAs).",
            "workflow": "Inspect/modify ComfyUI patches and workflow-level adjustments.",
            "version": "Review package history, diffs, and audit trail.",
            "rationale": "Read optimisation reasoning and trade-offs.",
            "discard": "Clear the current package and reset.",
            "status": "Show locked vs pending fields.",
            "unlock": "Unlock fields (unlock: <field> or unlock: all).",
            "help": "Show this reference.",
            "contact": "Link to creator profile (@ResistAiArt)."
        },
        "config": {
            "sampler": "Choose algorithm (Euler, DPM++, etc).",
            "steps": "Number of diffusion iterations.",
            "cfg": "Guidance scale (higher = stricter prompt adherence).",
            "resolution": "Width × height in pixels.",
            "seed": "Reproducibility control.",
            "LoRA": "Attach or remove fine-tune adapters.",
            "back": "Return to main.",
            "contact": "Creator profile (@ResistAiArt)."
        }
    }

def forge_package(req: OptimiseRequest, overrides: Optional[Dict[str, Any]] = None) -> ForgePackage:
    cleaned_prompt, safety_info = apply_safety(req.prompt)
    config = build_config(overrides)

    return ForgePackage(
        package_version="v2.1",
        positive=f"{cleaned_prompt}, vibrant colors, high detail",
        negative="lowres, blurry, overexposed, watermark, text",
        config=config,
        workflow_patch=build_workflow_patch(config),
        safety=safety_info,
        resources={"checkpoint": "Stale", "loras": [], "vae": "native"},
        menus=build_menus(),
        menus_help=build_menus_help(),
        prompt_suggestions=[
            "Shorten descriptors for better alignment with SDXL models.",
            "Emphasise subject over background when using anime checkpoints."
        ],
        workflow_suggestions=[
            "Consider Euler sampler for more fluid detail.",
            "Switch to Heun for smoother video frame consistency."
        ],
        package_goal=req.package_goal
    )

# ---------------------------------------------------------
# Routes
# ---------------------------------------------------------
@app.post("/optimise", response_model=ForgePackage)
async def optimise(req: OptimiseRequest, api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid or missing API key")
    try:
        package = forge_package(req)
        return package.dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimisation error: {str(e)}")


@app.post("/verify")
async def verify(resources: Dict[str, Any], api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid or missing API key")
    # Future: verify sha256 + licence info
    return {"status": "verified", "resources": resources}


@app.post("/caption")
async def caption(req: OptimiseRequest, api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid or missing API key")

    captions = {
        "hooks": [
            f"{req.prompt} — rendered by The Forge 🔥",
            f"What if {req.prompt.lower()}?"
        ],
        "narratives": [
            f"A Forge-optimised vision: {req.prompt}.",
            f"Creative output tuned for {req.package_goal.upper()} workflows."
        ],
        "technical": [
            "Generated with Forge Optimised Prompt Package.",
            "Configs: DPM++ 2M Karras | Steps: 30 | CFG: 7.0 | Res: 1024x768"
        ],
        "alt_text": f"{req.prompt}, styled for {req.package_goal.upper()}",
        "hashtags": ["#AIart", "#TheForge", "#ResistAiArt"]
    }

    return {"captions": captions}
