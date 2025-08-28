# main.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Literal, Dict, Any
import logging
import os
import uvicorn

from forge_prompts import optimise_prompt_package
from forge_image_analysis import analyse_image

# ------------------------------
# Logging
# ------------------------------
logging.basicConfig(level=logging.INFO, format="[Forge] %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# ------------------------------
# FastAPI setup
# ------------------------------
app = FastAPI(title="Forge Service API", version="1.0")

# Allow CORS (tighten this in prod!)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------
# Request + Response Models
# ------------------------------
class OptimiseRequest(BaseModel):
    package_goal: str = Field(..., description="Goal for the package, e.g., t2i or t2v")
    prompt: str = Field(..., description="Prompt to optimise")
    resources: Optional[List[dict]] = Field(default_factory=list, description="Resources to include")
    caption: Optional[str] = Field("", description="Optional caption context")

class AnalyseRequest(BaseModel):
    image_url: HttpUrl = Field(..., description="Image to analyse")
    mode: Literal["basic", "detailed"] = Field("basic", description="Analysis mode")

class StandardResponse(BaseModel):
    outcome: Literal["success", "error"]
    result: Optional[Dict[str, Any]] = None
    message: Optional[str] = None

# ------------------------------
# Endpoints
# ------------------------------
@app.post("/optimise", response_model=StandardResponse)
@app.post("/t2i", response_model=StandardResponse)  # alias
@app.post("/t2v", response_model=StandardResponse)  # alias
async def optimise(request: OptimiseRequest):
    """Optimise a prompt package for Forge."""
    try:
        result = await run_in_threadpool(
            optimise_prompt_package,
            request.prompt,
            request.package_goal,
            request.resources,
            request.caption
        )
        logger.info("optimise success", extra={"goal": request.package_goal, "prompt_length": len(request.prompt)})
        return {"outcome": "success", "result": result, "message": None}
    except Exception as e:
        logger.error(f"optimise failed: {str(e)}", exc_info=True)
        return {"outcome": "error", "result": None, "message": f"optimise failed: {str(e)}"}

@app.post("/analyse_image", response_model=StandardResponse)
@app.post("/analyse", response_model=StandardResponse)  # alias
async def analyse(request: AnalyseRequest):
    """Analyse an image (basic or detailed)."""
    try:
        result = await run_in_threadpool(
            analyse_image,
            request.image_url,
            None,
            request.mode
        )
        logger.info("analyse success", extra={"mode": request.mode})
        return {"outcome": "success", "result": result, "message": None}
    except Exception as e:
        logger.error(f"analyse failed: {str(e)}", exc_info=True)
        return {"outcome": "error", "result": None, "message": f"analyse failed: {str(e)}"}

@app.get("/health", response_model=StandardResponse)
async def health():
    """Simple health probe."""
    return {"outcome": "success", "result": {"status": "healthy"}, "message": None}

# ------------------------------
# Global Exception Handler
# ------------------------------
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=StandardResponse(outcome="error", result=None, message="internal failure").dict()
    )

# ------------------------------
# Run
# ------------------------------
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=os.getenv("ENV") == "development"
    )
