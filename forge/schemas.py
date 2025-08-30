# forge/schemas.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal

from forge.public_interface import PackageGoal


class OptimiseRequest(BaseModel):
    package_goal: PackageGoal
    prompt: str = Field(..., description="The input prompt")
    resources: Optional[List[dict]] = Field(default_factory=list, description="Optional resource list")
    caption: Optional[str] = Field("", description="Optional caption")
    custom_weights: Optional[Dict[str, float]] = Field(None, description="Custom keyword weights")


class AnalyseRequest(BaseModel):
    image_url: str = Field(..., description="The URL of the image to analyse")
    mode: Literal["basic", "detailed", "tags"] = Field("basic", description="Analysis mode")


class StandardResponse(BaseModel):
    outcome: Literal["success", "error"]
    result: Optional[dict] = None
    message: Optional[str] = None
