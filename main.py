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
from forge_resources import validate_resources

# --- settings ---
APP_NAME = "Forge Service API"
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# --- app init ---
app = FastAPI(title=APP_NAME, version="1.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten for prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# logging
logging.basicConfig(level=logging.INFO, format="[Forge] %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# --- request/response models ---
class OptimiseRequest(BaseModel):
    package_goal: str
    prompt: str
    resources: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    caption: Optional[str] = ""

class AnalyseRequest(BaseModel):
    image_url: str
    mode: Optional[str] = "basic"

class ApiResponse(BaseModel):
    outcome: str
    result: Optional[Dict[str, Any]] = None
    message: Optional[str] = None

# --- endpoints ---
@app.post("/optimise", response_model=ApiResponse)
@app.post("/t2i", response_model=ApiResponse)
@app.post("/t2v", response_model=ApiResponse)
async def optimise(request: OptimiseRequest):
    """
    forge builds optimised prompt package for [t2i] or [t2v]
    resources auto-validated with warnings + stats
    """
    try:
        # validate resources if any
        resource_report = validate_resources(request.resources) if request.resources else None

        result = await run_in_threadpool(
            optimise_prompt_package,
            request.prompt,
            request.package_goal,
            request.resources,
            request.caption,
        )

        if resource_report:
            result["resource_validation"] = resource_report

        return ApiResponse(outcome="success", result=result)

    except Exception as e:
        logger.error(f"optimise failed: {str(e)}")
        return JSONResponse(
            status_code=500,
            content=ApiResponse(outcome="error", message=f"optimise failed {str(e)}").dict(),
        )

@app.post("/analyse_image", response_model=ApiResponse)
@app.post("/analyse", response_model=ApiResponse)
async def analyse(request: AnalyseRequest):
    """
    forge analyses image in [basic] or [detailed] mode
    """
    try:
        result = await run_in_threadpool(analyse_image, request.image_url, None, request.mode)
        return ApiResponse(outcome="success", result=result)

    except Exception as e:
        logger.error(f"analyse failed: {str(e)}")
        return JSONResponse(
            status_code=500,
            content=ApiResponse(outcome="error", message=f"analyse failed {str(e)}").dict(),
        )

@app.get("/health", response_model=ApiResponse)
async def health():
    """
    forge health probe
    """
    return ApiResponse(outcome="success", message="healthy")

# --- fallback handler ---
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"unhandled error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content=ApiResponse(outcome="error", message="internal failure").dict(),
    )

# --- run ---
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=DEBUG)
