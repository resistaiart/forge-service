# routes/contracts.py
from fastapi import APIRouter
from fastapi.responses import FileResponse, JSONResponse
import os

router = APIRouter()


@router.get("/contracts", response_class=FileResponse)
async def serve_contracts():
    """
    Serve the Forge API contracts (JSON Schema).
    """
    contracts_path = os.path.join("contracts", "forge_contracts.json")
    if not os.path.exists(contracts_path):
        return JSONResponse(
            status_code=404,
            content={"outcome": "error", "message": "contracts schema not found"},
        )
    return FileResponse(contracts_path, media_type="application/json")
