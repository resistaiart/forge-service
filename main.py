# main.py
import os
import datetime
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Literal, Dict, Any
import uvicorn

# --- Forge Modules ---
from forge_prompts import optimise_prompt_package
from forge_image_analysis import analyse_image

# --- Forge Constants ---
FORGE_VERSION = "1.0.0"
FORGE_GIT_HASH = os.getenv("GIT_HASH", "unknown")
FORGE_BUILD_TIME = os.getenv("BUILD_TIME", datetime.datetime.utcnow().isoformat())

# --- Logging ---
logging.basicConfig(level=logging.INFO, format="[Forge] %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# --- FastAPI Setup ---
app = FastAPI(title="Forge Service API", version=FORGE_VERSION)

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # TODO: tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Request/Response Models ---
class OptimiseRequest(BaseModel):
    package_goal: str = Field(..., description="The goal for the prompt package (t2i, t2v, etc.)")
    prompt: str = Field(..., description="The initial prompt to optimise")
    resources: Optional[List[dict]] = Field(default_factory=list, description="Optional resource objects")
    caption: Optional[str] = Field("", description="Optional caption for context")

class AnalyseRequest(BaseModel):
    image_url: HttpUrl = Field(..., description="The image URL to analyse")
    mode: Literal["basic", "detailed"] = Field("basic", description="Analysis mode")

class StandardResponse(BaseModel):
    outcome: Literal["success", "error"]
    result: Optional[Dict[str, Any]] = None
    message: Optional[str] = None

# --- Routes ---
@app.post("/optimise", response_model=StandardResponse)
@app.post("/t2i", response_model=StandardResponse)  # alias
@app.post("/t2v", response_model=StandardResponse)  # alias
async def optimise(request: OptimiseRequest):
    """
    Optimise prompt package for text-to-image (t2i) or text-to-video (t2v).
    """
    try:
        result = await run_in_threadpool(
            optimise_prompt_package,
            request.prompt,
            request.package_goal,
            request.resources,
            request.caption,
        )
        return StandardResponse(outcome="success", result=result, message="optimise ok")
    except Exception as e:
        logger.error(f"optimise failed: {str(e)}", exc_info=True)
        return StandardResponse(outcome="error", message=f"optimise failed: {str(e)}")

@app.post("/analyse_image", response_model=StandardResponse)
@app.post("/analyse", response_model=StandardResponse)  # alias
async def analyse(request: AnalyseRequest):
    """
    Analyse image in [basic] or [detailed] mode.
    """
    try:
        result = await run_in_threadpool(
            analyse_image,
            request.image_url,
            None,
            request.mode,
        )
        return StandardResponse(outcome="success", result=result, message="analyse ok")
    except Exception as e:
        logger.error(f"analyse failed: {str(e)}", exc_info=True)
        return StandardResponse(outcome="error", message=f"analyse failed: {str(e)}")

@app.get("/health", response_model=StandardResponse)
async def health():
    """
    Forge health probe.
    """
    return StandardResponse(outcome="success", message="healthy")

@app.get("/version", response_model=StandardResponse)
async def version():
    """
    Forge version info for syncing frontend/backend and debugging.
    """
    version_info = {
        "semantic": FORGE_VERSION,
        "git_hash": FORGE_GIT_HASH,
        "build_time": FORGE_BUILD_TIME,
    }
    return StandardResponse(outcome="success", result=version_info, message="version info")

# --- Global Exception Handler ---
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=StandardResponse(outcome="error", message="internal failure").dict(),
    )

# --- Entrypoint ---
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
