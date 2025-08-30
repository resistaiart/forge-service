# routes/legacy.py
from fastapi import APIRouter, Request
from fastapi.concurrency import run_in_threadpool
import logging

from forge.schemas import OptimiseRequest, AnalyseRequest, StandardResponse
from forge_prompts import optimise_prompt_package
from forge_image_analysis import analyse_image
from forge.workflows import optimise_i2i_package, optimise_t2v_package

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/optimise", response_model=StandardResponse)
@router.post("/t2i", response_model=StandardResponse)
@router.post("/t2v", response_model=StandardResponse)
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


@router.post("/optimise/i2i", response_model=StandardResponse)
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
        return {"outcome": "error", "message": str(e)}


@router.post("/optimise/t2v", response_model=StandardResponse)
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
        return {"outcome": "error", "message": str(e)}


@router.post("/analyse", response_model=StandardResponse)
@router.post
