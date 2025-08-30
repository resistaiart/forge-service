# forge/config.py — Centralized settings and constants
import os
import logging
from typing import List
from dotenv import load_dotenv
from pydantic import BaseSettings, Field, validator

# Load .env if available
load_dotenv()

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    app_name: str = "Forge API"
    version: str = "v2.0"
    environment: str = Field(default="production", env="ENV")
    debug: bool = Field(default=False, env="DEBUG")

    port: int = Field(default=8000, env="PORT")
    cors_origins: List[str] = Field(default=["*"], env="CORS_ORIGINS")

    enable_legacy: bool = Field(default=True, env="FORGE_ENABLE_LEGACY")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @validator("cors_origins", pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    @validator("port")
    def validate_port(cls, v):
        if not (1 <= v <= 65535):
            raise ValueError("PORT must be between 1 and 65535")
        return v


settings = Settings()

# Used in `/version` endpoint
ENDPOINTS = {
    "legacy": [
        "/optimise", "/t2i", "/t2v",
        "/optimise/i2i", "/optimise/t2v", "/analyse"
    ],
    "sealed_workshop": ["/v2/optimise", "/v2/analyse"],
    "health": "/health",
    "version": "/version",
    "manifest": "/manifest"
}

logger.info(f"Loaded config for {settings.app_name} v{settings.version} on port {settings.port}")
