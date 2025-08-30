# main.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
import uvicorn
import logging
import os

# Forge imports (aligned with repo structure)
from forge.prompts import optimise_prompt_package
from forge.image_analysis import analyse_image
from forge.workflows import optimise_i2i_package, optimise_t2v_package
from forge.optimizer import optimise_sealed
from forge.public_interface import PackageGoal
from forge.safety import enforce_safety

# =====================
# SETTINGS
# =====================
class Settings(BaseModel):
    app_name: str = "Forge Service API"
    cors_origins: str = os.getenv("CORS_ORIGINS", "*")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"

settings = Settings()

# =====================
# APP INIT
# =====================
app = FastAPI(title=settings.app_name, version="2.0")

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
# MODELS
# =====================
class OptimiseRequest(BaseModel):
    package_goal: PackageGoal
    prompt: str = Field(..., description="The input prompt")
    resources: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Optional resources")
    caption: Optional[str] = Field("", description="Optional caption")
    custom_weights: Optional[Dict[str, float]] = Field(None, description="Custom keyword weights")

class AnalyseRequest(BaseModel):
    image_url: str = Field(..., description="The image URL to analyse")
    mode: Literal["basic", "detailed", "tags"] = Field("basic", description="Analysis mode")

class StandardResponse(BaseModel):
    outcome: Literal["success", "error"]
    result: Optional[Dict[str, Any]] = None
    message: Optional[str] = None

# =====================
# ROUTES
# =====================
@app.post("/v2/optimise", response_model=StandardResponse)
async def optimise_v2(request: OptimiseRequest):
    try:
        logger.info(f"Optimisation request: {request.package_goal}")
        request_dict = request.dict()

        # Safety check before processing
        if not enforce_safety(request_dict):
            return {"outcome": "error", "message": "Request failed safety validation"}

        result = await run_in_threadpool(optimise_sealed, request_dict)
        return {"outcome": "success", "result": result}

    except Exception as e:
        logger.error(f"Optimisation error: {e}")
        return {"outcome": "error", "message": f"Internal error: {str(e)}"}

@app.post("/v2/analyse", response_model=StandardResponse)
async def analyse_v2(request: AnalyseRequest):
    try:
        logger.info(f"Image analysis request: {request.image_url}")
        result = await run_in_threadpool(analyse_image, request.image_url, request.mode)
        return {"outcome": "success", "result": result}
    except Exception as e:
        logger.error(f"Image analysis error: {e}")
        return {"outcome": "error", "message": f"Analysis failed: {str(e)}"}

@app.post("/optimise", response_model=StandardResponse)
@app.post("/t2i", response_model=StandardResponse)
@app.post("/t2v", response_model=StandardResponse)
async def optimise_legacy(request: OptimiseRequest):
    try:
        logger.info(f"Legacy optimisation request: {request.package_goal}")
        result = await run_in_threadpool(
            optimise_prompt_package,
            request.prompt,
            request.package_goal,
            request.resources,
            request.caption,
            request.custom_weights,
        )
        return {"outcome": "success", "result": result}
    except Exception as e:
        logger.error(f"Legacy optimisation error: {e}")
        return {"outcome": "error", "message": f"Legacy optimisation failed: {str(e)}"}

@app.post("/optimise/i2i", response_model=StandardResponse)
async def optimise_i2i(request: Request):
    try:
        payload = await request.json()
        result = await run_in_threadpool(
            optimise_i2i_package,
            payload.get("prompt"),
            payload.get("input_image"),
            payload.get("denoise_strength", 0.75),
            payload.get("resources", []),
            payload.get("caption", ""),
        )
        return {"outcome": "success", "result": result}
    except Exception as e:
        logger.error(f"I2I optimisation error: {e}")
        return {"outcome": "error", "message": f"I2I failed: {str(e)}"}

@app.post("/optimise/t2v", response_model=StandardResponse)
async def optimise_t2v(request: Request):
    try:
        payload = await request.json()
        result = await run_in_threadpool(
            optimise_t2v_package,
            payload.get("prompt"),
            payload.get("num_frames", 25),
            payload.get("fps", 6),
            payload.get("motion_intensity", "medium"),
            payload.get("resources", []),
            payload.get("caption", ""),
        )
        return {"outcome": "success", "result": result}
    except Exception as e:
        logger.error(f"T2V optimisation error: {e}")
        return {"outcome": "error", "message": f"T2V failed: {str(e)}"}

@app.get("/health", response_model=StandardResponse)
async def health():
    return {"outcome": "success", "message": "healthy"}

@app.get("/version")
async def version():
    return {
        "version": "2.0",
        "service": "Forge API",
        "endpoints": [
            "/v2/optimise",
            "/v2/analyse",
            "/optimise",
            "/t2i",
            "/t2v",
            "/optimise/i2i",
            "/optimise/t2v",
            "/health",
            "/manifest"
        ]
    }

@app.get("/manifest", response_class=FileResponse)
async def manifest():
    return FileResponse("forge_manifest.json", media_type="application/json")

# =====================
# ERROR HANDLER
# =====================
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}")
    return JSONResponse(status_code=500, content={"outcome": "error", "message": "internal failure"})

# =====================
# RUN
# =====================
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
