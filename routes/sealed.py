# routes/sealed.py
from fastapi import APIRouter
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import JSONResponse
import logging

from forge.optimizer import optimise_sealed
from forge.image_analysis import analyse_sealed
from forge.schemas import OptimiseRequest, AnalyseRequest, StandardResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/v2/optimise", response_model=StandardResponse)
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


@router.post("/v2/analyse", response_model=StandardResponse)
async def analyse_v2(request: AnalyseRequest):
    try:
        logger.info(f"Sealed analysis: {request.image_url}")
        result = await run_in_threadpool(analyse_sealed, request.dict())
        return {"outcome": "success", "result": result}
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        return {"outcome": "error", "message": "Internal analysis error"}
