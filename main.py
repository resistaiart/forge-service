# main.py
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
import uvicorn
import logging
import os

# Import existing modules
from forge_prompts import optimise_prompt_package
from forge_image_analysis import analyse_image, analyse_sealed   # 🔥 added analyse_sealed
from forge_workflows import optimise_i2i_package, optimise_t2v_package, optimise_i2v_package

# Import new sealed workshop orchestration
from forge_optimizer import optimize_sealed
from forge_public_interface import PackageGoal

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
# REQUEST/RESPONSE MODELS
# =====================
class OptimiseRequest(BaseModel):
    package_goal: PackageGoal
    prompt: str = Field(..., description="The input prompt")
    resources: Optional[List[dict]] = Field(default_factory=list, description="Optional resource list")
    caption: Optional[str] = Field("", description="Optional caption")
    custom_weights: Optional[Dict[str, float]] = Field(None, description="Custom keyword weights")

class AnalyseRequest(BaseModel):
    image_url: str = Field(..., description="The URL of the image to analyse")
    mode: Literal["basic", "detailed"] = Field("basic", description="Analysis mode")

class StandardResponse(BaseModel):
    outcome: Literal["success", "error"]
    result: Optional[dict] = None
    message: Optional[str] = None

# =====================
# ROUTES - SEALED WORKSHOP (NEW)
# =====================
@app.post("/v2/optimise", response_model=StandardResponse)
async def optimise_v2(request: OptimiseRequest):
    try:
        logger.info(f"Sealed workshop request: {request.package_goal}")
        request_dict = request.dict()
        result = await run_in_threadpool(optimize_sealed, request_dict)
        return {"outcome": "success", "result": result}
    except ValueError as e:
        if "Content violation" in str(e):
            return JSONResponse(status_code=400, content={"outcome": "error", "message": f"Content blocked: {str(e)}"})
        logger.error(f"Validation error in sealed workshop: {e}")
        return {"outcome": "error", "message": f"Validation error: {str(e)}"}
    except Exception as e:
        logger.error(f"Sealed workshop error: {e}")
        return {"outcome": "error", "message": f"Internal optimization error: {str(e)}"}

@app.post("/v2/analyse", response_model=StandardResponse)   # 🔥 NEW sealed route
async def analyse_v2(request: AnalyseRequest):
    try:
        logger.info(f"Sealed analysis request: {request.image_url}")
        request_dict = request.dict()
        result = await run_in_threadpool(analyse_sealed, request_dict)
        return {"outcome": "success", "result": result}
    except Exception as e:
        logger.error(f"Sealed analysis error: {e}")
        return {"outcome": "error", "message": f"Internal analysis error: {str(e)}"}

# =====================
# ROUTES - LEGACY ENDPOINTS
# =====================
@app.post("/optimise", response_model=StandardResponse)
@app.post("/t2i", response_model=StandardResponse)
@app.post("/t2v", response_model=StandardResponse)
async def optimise_legacy(request: OptimiseRequest):
    try:
        logger.info(f"Legacy optimization request: {request.package_goal}")
        result = await run_in_threadpool(
            optimise_prompt_package,
            request.prompt,
            request.package_goal,
            request.resources,
            request.caption,
            request.custom_weights
        )
        return {"outcome": "success", "result": result}
    except Exception as e:
        logger.error(f"Legacy optimization failed: {e}")
        return {"outcome": "error", "message": f"Optimization failed: {str(e)}"}

@app.post("/optimise/i2i", response_model=StandardResponse)
async def optimise_i2i_legacy(request: Request):
    try:
        payload = await request.json()
        result = await run_in_threadpool(
            optimise_i2i_package,
            payload.get("prompt"),
            payload.get("input_image"),
            payload.get("denoise_strength", 0.75),
            payload.get("resources", []),
            payload.get("caption", "")
        )
        return {"outcome": "success", "result": result}
    except Exception as e:
        logger.error(f"I2I optimization failed: {e}")
        return {"outcome": "error", "message": f"I2I optimization failed: {str(e)}"}

@app.post("/optimise/t2v", response_model=StandardResponse)
async def optimise_t2v_legacy(request: Request):
    try:
        payload = await request.json()
        result = await run_in_threadpool(
            optimise_t2v_package,
            payload.get("prompt"),
            payload.get("num_frames", 25),
            payload.get("fps", 6),
            payload.get("motion_intensity", "medium"),
            payload.get("resources", []),
            payload.get("caption", "")
        )
        return {"outcome": "success", "result": result}
    except Exception as e:
        logger.error(f"T2V optimization failed: {e}")
        return {"outcome": "error", "message": f"T2V optimization failed: {str(e)}"}

@app.post("/analyse_image", response_model=StandardResponse)
@app.post("/analyse", response_model=StandardResponse)
async def analyse(request: AnalyseRequest):
    try:
        result = await run_in_threadpool(analyse_image, request.image_url, None, request.mode)
        return {"outcome": "success", "result": result}
    except Exception as e:
        logger.error(f"Image analysis failed: {e}")
        return {"outcome": "error", "message": f"Image analysis failed: {str(e)}"}

# =====================
# HEALTH & UTILITY ENDPOINTS
# =====================
@app.get("/health", response_model=StandardResponse)
async def health():
    return {"outcome": "success", "message": "healthy"}

@app.get("/version")
async def version():
    return {
        "version": "2.0",
        "service": "The Forge API",
        "endpoints": {
            "legacy": "/optimise, /t2i, /t2v, /optimise/i2i, /optimise/t2v",
            "sealed_workshop": "/v2/optimise, /v2/analyse",
            "analysis": "/analyse",
            "health": "/health",
            "manifest": "/manifest"
        }
    }

@app.get("/manifest", response_class=FileResponse)
async def serve_manifest():
    """Serve the full Forge manifest as raw JSON"""
    return FileResponse("forge_manifest.json", media_type="application/json")

# =====================
# ERROR FALLBACK
# =====================
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {str(exc)}")
    return JSONResponse(status_code=500, content={"outcome": "error", "message": "internal failure"})

# =====================
# RUN
# =====================
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
