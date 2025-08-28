# main.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Any, Literal
import uvicorn
import logging
import os

from forge_prompts import optimise_prompt_package
from forge_image_analysis import analyse_image

# =====================
# SETTINGS
# =====================
class Settings(BaseModel):
    app_name: str = "Forge Service API"
    cors_origins: str = os.getenv("CORS_ORIGINS", "*")
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"

settings = Settings()

# =====================
# APP INIT
# =====================
app = FastAPI(title=settings.app_name, version="1.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging
logging.basicConfig(level=logging.INFO, format="[Forge] %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# =====================
# REQUEST/RESPONSE MODELS
# =====================
class OptimiseRequest(BaseModel):
    package_goal: Literal["t2i", "t2v", "upscale"] = Field(..., description="Generation goal")
    prompt: str = Field(..., description="The input prompt")
    resources: Optional[List[dict]] = Field(default_factory=list, description="Optional resource list")
    caption: Optional[str] = Field("", description="Optional caption")
    custom_weights: Optional[Dict[str, float]] = Field(None, description="Custom keyword weights")
    checkpoint: Optional[str] = Field(None, description="Checkpoint file or name")

class AnalyseRequest(BaseModel):
    image_url: HttpUrl = Field(..., description="The URL of the image to analyse")
    mode: Literal["basic", "detailed"] = Field("basic", description="Analysis mode")

class StandardResponse(BaseModel):
    outcome: Literal["success", "error"]
    result: Optional[dict] = None
    message: Optional[str] = None

# =====================
# ROUTES
# =====================
@app.post("/optimise", response_model=StandardResponse)
@app.post("/t2i", response_model=StandardResponse)  # alias
@app.post("/t2v", response_model=StandardResponse)  # alias
async def optimise(request: OptimiseRequest):
    """
    Optimise prompt package for [t2i], [t2v], or [upscale].
    Includes checkpoint-aware suggestions via CivitAI.
    """
    try:
        result = await run_in_threadpool(
            optimise_prompt_package,
            request.prompt,
            request.package_goal,
            request.resources,
            request.caption,
            request.custom_weights,
            request.checkpoint  # NEW: pass checkpoint through
        )
        return {"outcome": "success", "result": result}

    except Exception as e:
        logger.error(f"optimise failed: {str(e)}", exc_info=True)
        return {"outcome": "error", "message": f"optimise failed: {str(e)}"}

@app.post("/analyse_image", response_model=StandardResponse)
@app.post("/analyse", response_model=StandardResponse)  # alias
async def analyse(request: AnalyseRequest):
    """
    Analyse an image in [basic] or [detailed] mode.
    """
    try:
        result = await run_in_threadpool(analyse_image, request.image_url, None, request.mode)
        return {"outcome": "success", "result": result}

    except Exception as e:
        logger.error(f"analyse failed: {str(e)}", exc_info=True)
        return {"outcome": "error", "message": f"analyse failed: {str(e)}"}

@app.get("/health", response_model=StandardResponse)
async def health():
    """
    Forge health probe.
    """
    return {"outcome": "success", "message": "healthy"}

# =====================
# ERROR FALLBACK
# =====================
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content=StandardResponse(outcome="error", message="internal failure").dict()
    )

# =====================
# RUN
# =====================
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")), reload=settings.debug)
