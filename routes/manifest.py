# routes/manifest.py
from fastapi import APIRouter
from fastapi.responses import JSONResponse, FileResponse
import os
import json

router = APIRouter()


@router.get("/manifest", response_class=FileResponse)
async def serve_manifest():
    """Serve the lightweight Forge runtime manifest."""
    manifest_path = os.path.join("forge_manifest.json")
    if not os.path.exists(manifest_path):
        return JSONResponse(
            status_code=404,
            content={"outcome": "error", "message": "manifest not found"},
        )
    return FileResponse(manifest_path, media_type="application/json")


@router.get("/manifest/full")
async def serve_full_manifest():
    """Serve a merged manifest (runtime manifest + contracts schema)."""
    manifest_path = os.path.join("forge_manifest.json")
    contracts_path = os.path.join("contracts", "forge_contracts.json")

    try:
        with open(manifest_path, "r") as f:
            manifest_data = json.load(f)
    except Exception:
        return JSONResponse(
            status_code=404,
            content={"outcome": "error", "message": "manifest not found"},
        )

    try:
        with open(contracts_path, "r") as f:
            contracts_data = json.load(f)
    except Exception:
        contracts_data = {"error": "contracts not found"}

    return {
        "manifest": manifest_data,
        "contracts": contracts_data,
    }
