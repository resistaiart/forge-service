from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

app = FastAPI(title="Forge API", version="2.0.0")

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
    """
    Safety filter: enforce NSFW rules, auto-clean IP/minor-coded tokens.
    """
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
        package_version="v2.0",
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
# Middleware – API Key
# ---------------------------------------------------------

API_KEY = "supersecret"  # TODO: load from environment in production

@app.middleware("http")
async def require_api_key(request: Request, call_next):
    if request.url.path.startswith("/optimise") or request.url.path.startswith("/verify"):
        api_key = request.headers.get("x-api-key")
        if not api_key or api_key != API_KEY:
            return JSONResponse(
                status_code=403,
                content={"error": "Forbidden", "details": "Invalid or missing API key"},
            )
    return await call_next(request)


# ---------------------------------------------------------
# Routes
# ---------------------------------------------------------

@app.post("/optimise", response_model=ForgePackage)
async def optimise(req: OptimiseRequest):
    try:
        package = forge_package(req)
        return package.dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimisation error: {str(e)}")


@app.post("/verify")
async def verify(resources: Dict[str, Any]):
    return {"status": "verified", "resources": resources}


@app.post("/caption")
async def caption(req: OptimiseRequest):
    return {
        "captions": [
            f"Prompt: {req.prompt}",
            "Alt text: futuristic skyline, neon reflections",
            "#aiart #cyberpunk #TheForge"
        ]
    }
