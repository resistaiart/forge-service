# main.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict
import uvicorn
import logging
import os

from forge_prompts import optimise_prompt_package
from forge_image_analysis import analyse_image

# ---- Settings ----
class Settings(BaseModel):
    app_name: str = "Forge Service API"
    cors_origins: str = os.getenv("CORS_ORIGINS", "*")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"

settings = Settings()

# ---- Forge API ----
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

# ---- Request / Response Models ----
class OptimiseRequest(BaseModel):
    package_goal: str
    prompt: str
    resources: Optional[List[str]] = Field(default_factory=list)
    caption: Optional[str] = ""

class AnalyseRequest(BaseModel):
    image_url: str
    mode: Optional[str] = "basic"

class ApiResponse(BaseModel):
    outcome: str
    result: Optional[Dict[str, Any]] = None
    message: Optional[str] = None

# ---- Endpoints ----
@app.post("/optimise", response_model=ApiResponse)
@app.post("/t2i", response_model=ApiResponse)  # alias
@app.post("/t2v", response_model=ApiResponse)  # alias
async def optimise(request: OptimiseRequest):
    """
    Optimise a prompt package for [t2i] or [t2v].
    """
    try:
        result = await run_in_threadpool(
            optimise_prompt_package,
            request.package_goal,
            request.prompt,
            request.resources,
            request.caption
        )
        return ApiResponse(outcome="success", result=result)

    except Exception as e:
        logger.error(f"optimise failed: {str(e)}")
        return JSONResponse(
            status_code=500,
            content=ApiResponse(outcome="error", message=f"optimise failed {str(e)}").dict()
        )

@app.post("/analyse_image", response_model=ApiResponse)
@app.post("/analyse", response_model=ApiResponse)  # alias
async def analyse(request: AnalyseRequest):
    """
    Analyse an image in [basic] or [detailed] mode.
    """
    try:
        result = await run_in_threadpool(analyse_image, request.image_url, None, request.mode)
        return ApiResponse(outcome="success", result=result)

    except Exception as e:
        logger.error(f"analyse failed: {str(e)}")
        return JSONResponse(
            status_code=500,
            content=ApiResponse(outcome="error", message=f"analyse failed {str(e)}").dict()
        )

@app.get("/health", response_model=ApiResponse)
async def health():
    """
    Forge health probe.
    """
    return ApiResponse(outcome="success", message="healthy")

# ---- Global Error Handler ----
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content=ApiResponse(outcome="error", message="internal failure").dict()
    )

# ---- Run ----
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=settings.debug)
