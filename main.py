# main.py
import os
import logging
from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Literal, Any, Dict
import uvicorn
from slowapi import Limiter
from slowapi.util import get_remote_address
from dotenv import load_dotenv

# Forge modules
from forge_prompts import optimise_prompt_package
from forge_image_analysis import analyse_image

# --- Load .env ---
load_dotenv()

# --- Settings ---
class Settings(BaseModel):
    app_name: str = "Forge Service API"
    cors_origins: str = os.getenv("CORS_ORIGINS", "*")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"

settings = Settings()

# --- Forge API instance ---
app = FastAPI(title=settings.app_name, version="1.0")

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Rate Limiting ---
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# --- Logging ---
logging.basicConfig(level=logging.INFO, format="[Forge] %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# --- Pydantic Models ---
class OptimiseRequest(BaseModel):
    package_goal: str = Field(..., description="Generation goal (e.g. t2i, t2v)")
    prompt: str = Field(..., description="The initial prompt to optimise")
    resources: Optional[List[dict]] = Field(default_factory=list)
    caption: Optional[str] = ""

class AnalyseRequest(BaseModel):
    image_url: HttpUrl
    mode: Literal["basic", "detailed"] = "basic"

class StandardResponse(BaseModel):
    outcome: Literal["success", "error"]
    result: Optional[Dict[str, Any]] = None
    message: Optional[str] = None

# --- Endpoints ---
@app.post("/optimise", response_model=StandardResponse)
@app.post("/t2i", response_model=StandardResponse)
@app.post("/t2v", response_model=StandardResponse)
@limiter.limit("5/minute")
async def optimise(request: OptimiseRequest):
    """
    Optimise prompt package for t2i or t2v.
    """
    try:
        logger.info("optimise request received", extra={
            "goal": request.package_goal,
            "prompt_length": len(request.prompt)
        })
        result = await run_in_threadpool(
            optimise_prompt_package,
            request.prompt,
            request.package_goal,
            request.resources,
            request.caption
        )
        return {"outcome": "success", "result": result}
    except Exception as e:
        logger.error(f"optimise failed: {str(e)}", exc_info=True)
        return {"outcome": "error", "message": f"optimise failed: {str(e)}"}

@app.post("/analyse_image", response_model=StandardResponse)
@app.post("/analyse", response_model=StandardResponse)
@limiter.limit("5/minute")
async def analyse(request: AnalyseRequest):
    """
    Analyse image in [basic] or [detailed] mode.
    """
    try:
        logger.info("analyse request received", extra={"mode": request.mode})
        result = await run_in_threadpool(analyse_image, request.image_url, request.mode)
        return {"outcome": "success", "result": result}
    except Exception as e:
        logger.error(f"analyse failed: {str(e)}", exc_info=True)
        return {"outcome": "error", "message": f"analyse failed: {str(e)}"}

@app.get("/health", response_model=StandardResponse)
async def health():
    """
    Forge health probe with system status.
    """
    try:
        import psutil
        return {
            "outcome": "success",
            "message": "healthy",
            "result": {
                "memory": f"{psutil.virtual_memory().percent}%",
                "cpu": f"{psutil.cpu_percent()}%"
            }
        }
    except Exception:
        return {"outcome": "success", "message": "healthy"}

# --- Global Error Fallback ---
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"outcome": "error", "message": "internal failure"}
    )

# --- Run (dev only) ---
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=settings.debug
    )
