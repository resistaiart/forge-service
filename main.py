from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
import uvicorn
import logging
import os

from forge.prompts import optimise_prompt_package
from forge.image_analysis import analyse_image, analyse_sealed
from forge.workflows import optimise_i2i_package, optimise_t2v_package
from forge.optimizer import optimise_sealed
from forge.public_interface import PackageGoal
from forge.config import ENDPOINTS  # ✅ Central config

# =====================
# SETTINGS
# =====================
class Settings(BaseModel):
    app_name: str = "Forge Service API"
    cors_origins: str = os.getenv("CORS_ORIGINS", "*")
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    enable_legacy: bool = os.getenv("FORGE_ENABLE_LEGACY", "true").lower() == "true"

settings = Settings()

# =====================
# APP INIT
# =====================
app = FastAPI(title=settings.app_name, version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO, format="[Forge] %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# =====================
# MODELS
# =====================
class OptimiseRequest(BaseModel):
    package_goal: PackageGoal
    prompt: str
    resources: Optional[List[dict]] = Field(default_factory=list)
    caption: Optional[str] = ""
    custom_weights: Optional[Dict[str, float]] = None

class AnalyseRequest(BaseModel):
    image_url: str
    mode: Literal["basic", "detailed", "tags"] = "basic"

class StandardResponse(BaseModel):
    outcome: Literal["success", "error"]
    result: Optional[dict] = None
    message: Optional[str] = None

# =====================
# SEALED ENDPOINTS
# =====================
@app.post("/v2/optimise", response_model=StandardResponse)
async def optimise_v2(request: OptimiseRequest):
    try:
        logger.info(f"Sealed workshop request: {request.package_goal}")
        result = await run_in_threadpool(optimise_sealed, request.dict())
        return {"outcome": "success", "result": result}
    except ValueError as e:
        if "Content violation" in str(e):
            return JSONResponse(status_code=400, content={"outcome": "error", "message": f"Content blocked: {str(e)}"})
        logger.error(f"Validation error: {e}")
        return {"outcome": "error", "message": str(e)}
    except Exception as e:
        logger.error(f"Internal error: {e}")
        return {"outcome": "error", "message": "Internal optimization error"}

@app.post("/v2/analyse", response_model=StandardResponse)
async def analyse_v2(request: AnalyseRequest):
    try:
        logger.info(f"Sealed analysis: {request.image_url}")
        result = await run_in_threadpool(analyse_sealed, request.dict())
        return {"outcome": "success", "result": result}
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        return {"outcome": "error", "message": "Internal analysis error"}

# =====================
# LEGACY ROUTES (Optional)
# =====================
if settings.enable_legacy:
    @app.post("/optimise", response_model=StandardResponse)
    @app.post("/t2i", response_model=StandardResponse)
    @app.post("/t2v", response_model=StandardResponse)
    async def optimise_legacy(request: OptimiseRequest):
        try:
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
            return {"outcome": "error", "message": str(e)}

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
            logger.error(f"I2I failed: {e}")
            return {"outcome": "error", "message": str(e)}

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
            logger.error(f"T2V failed: {e}")
            return {"outcome": "error", "message": str(e)}

    @app.post("/analyse", response_model=StandardResponse)
    async def analyse(request: AnalyseRequest):
        try:
            result = await run_in_threadpool(analyse_image, request.image_url, None, request.mode)
            return {"outcome": "success", "result": result}
        except Exception as e:
            logger.error(f"Legacy analysis failed: {e}")
            return {"outcome": "error", "message": str(e)}

# =====================
# HEALTH & MANIFEST
# =====================
@app.get("/health", response_model=StandardResponse)
async def health():
    return {"outcome": "success", "message": "healthy"}

@app.get("/version")
async def version():
    return {"version": "2.0", "service": "The Forge API", "endpoints": ENDPOINTS}

@app.get("/manifest", response_class=FileResponse)
async def serve_manifest():
    return FileResponse("forge_manifest.json", media_type="application/json")

# =====================
# GLOBAL ERROR HANDLER
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
