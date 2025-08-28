# main.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool
import uvicorn
import logging

from forge_prompts import optimise_prompt_package
from forge_image_analysis import analyse_image

# Forge API instance
app = FastAPI(title="Forge Service API", version="1.0")

# CORS (safe for now, restrict origins in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging setup
logging.basicConfig(level=logging.INFO, format="[Forge] %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


@app.post("/optimise")
async def optimise(request: Request):
    """
    Optimise prompt package for [t2i], [t2v], etc.
    """
    try:
        payload = await request.json()
        package_goal = payload.get("package_goal")
        prompt = payload.get("prompt")
        resources = payload.get("resources", [])
        caption = payload.get("caption", "")

        if not package_goal or not prompt:
            return JSONResponse(
                status_code=400,
                content={"error": "missing: package_goal and prompt"}
            )

        result = await run_in_threadpool(
            optimise_prompt_package,
            package_goal,
            prompt,
            resources,
            caption
        )
        return result

    except Exception as e:
        logger.error(f"optimise failed: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"optimise failed: {str(e)}"}
        )


@app.post("/analyse_image")
async def analyse(request: Request):
    """
    Analyse image in [basic] (fast) or [detailed] (deep) mode.
    """
    try:
        payload = await request.json()
        image_url = payload.get("image_url")
        mode = payload.get("mode", "basic")

        if not image_url:
            return JSONResponse(
                status_code=400,
                content={"error": "missing: image_url"}
            )

        result = await run_in_threadpool(analyse_image, image_url, None, mode)
        return result

    except Exception as e:
        logger.error(f"analyse failed: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"analyse failed: {str(e)}"}
        )


@app.get("/health")
async def health():
    """
    Health check endpoint.
    """
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
