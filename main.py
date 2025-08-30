
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel
import uvicorn
import logging
import os

from forge.config import settings
from forge.schemas import StandardResponse
from forge.public_interface import is_valid_goal

# =====================
# INIT
# =====================
app = FastAPI(title=settings.app_name, version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO, format="[Forge] %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# =====================
# ROUTES (Modular)
# =====================
from routes import sealed
app.include_router(sealed.router)

from routes import legacy
app.include_router(legacy.router)

from routes import manifest
app.include_router(manifest.router)

from routes import health
app.include_router(health.router)

# =====================
# ROUTES - PACKAGE GOAL VALIDATION
# =====================
@app.post("/validate-package-goal", response_model=StandardResponse)
async def validate_package_goal(request: Request):
    body = await request.json()
    goal = body.get("package_goal")

    if goal and is_valid_goal(goal):
        return JSONResponse(status_code=200, content={"outcome": "success", "message": f"Valid goal: {goal}"})

    return JSONResponse(status_code=400, content={"outcome": "error", "message": f"Invalid goal: {goal}"})

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
    uvicorn.run("main:app", host="0.0.0.0", port=settings.port)
