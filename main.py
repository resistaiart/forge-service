# main.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool
import uvicorn
import logging

from forge_prompts import optimise_prompt_package
from forge_image_analysis import analyse_image

# Forge API
app = FastAPI(title="Forge Service API", version="1.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging
logging.basicConfig(level=logging.INFO, format="[Forge] %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


# ---------------------------
# ROUTES
# ---------------------------

@app.post("/optimise")
@app.post("/t2i")  # alias
@app.post("/t2v")  # alias
async def optimise(request: Request):
    """
    Optimise a prompt package for [t2i] or [t2v].
    """
    try:
        payload = await request.json()
        package_goal = payload.get("package_goal")
        prompt = payload.get("prompt")
        resources = payload.get("resources", [])
        caption = payload.get("caption", "")

        if not package_goal or not prompt:
            return {"outcome": "error", "message": "missing required fields: package_goal and prompt"}

        # Call optimiser (already returns {outcome, result, message})
        return await run_in_threadpool(
            optimise_prompt_package,
            prompt,
            package_goal,
            resources,
            caption
        )

    except Exception as e:
        logger.error(f"optimise failed: {str(e)}")
        return {"outcome": "error", "message": f"optimise failed: {str(e)}"}


@app.post("/analyse_image")
@app.post("/analyse")  # alias
async def analyse(request: Request):
    """
    Analyse image in [basic] or [detailed] mode.
    """
    try:
        payload = await request.json()
        image_url = payload.get("image_url")
        mode = payload.get("mode", "basic")

        if not image_url:
            return {"outcome": "error", "message": "missing required field: image_url"}

        # Call analyser (already returns {outcome, result, message})
        return await run_in_threadpool(analyse_image, image_url, mode=mode)

    except Exception as e:
        logger.error(f"analyse failed: {str(e)}")
        return {"outcome": "error", "message": f"analyse failed: {str(e)}"}


@app.get("/health")
async def health():
    """
    Forge health probe.
    """
    return {"outcome": "success", "message": "healthy"}


# ---------------------------
# GLOBAL ERROR HANDLER
# ---------------------------
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {str(exc)}")
    return JSONResponse(status_code=500, content={"outcome": "error", "message": "internal failure"})


# ---------------------------
# DEV ENTRY POINT
# ---------------------------
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
