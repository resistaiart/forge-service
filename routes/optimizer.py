# routes/optimizer.py — Optimisation endpoints
from fastapi import APIRouter, Request
from fastapi.concurrency import run_in_threadpool
from forge.services.optimizer import optimise_sealed_service
from forge.models.schemas import StandardResponse

router = APIRouter()

@router.post("/v2/optimise", response_model=StandardResponse)
async def optimise_sealed(request: Request) -> StandardResponse:
    try:
        payload = await request.json()
        result = await run_in_threadpool(optimise_sealed_service, payload)
        return StandardResponse(outcome="success", result=result)
    except Exception as e:
        return StandardResponse(outcome="error", result=None, message=str(e))
