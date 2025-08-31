import os
import logging
import json
from typing import List, Union
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator

# Load .env from the correct location
env_path = Path("forge-service") / ".env"
load_dotenv(env_path)

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    app_name: str = "Forge API"
    version: str = "v2.0"
    environment: str = Field(default="production", env="ENV")
    debug: bool = Field(default=False, env="DEBUG")

    port: int = Field(default=8000, env="PORT")
    # ✅ Accept str OR list, so env parsing never fails before validator
    cors_origins: Union[str, List[str]] = Field(default="*", env="CORS_ORIGINS")

    enable_legacy: bool = Field(default=True, env="FORGE_ENABLE_LEGACY")

    # Chroma DB Configuration
    chroma_server_host: str = Field(default="0.0.0.0", env="CHROMA_SERVER_HOST")
    chroma_server_http_port: int = Field(default=8000, env="CHROMA_SERVER_HTTP_PORT")
    chroma_server_grpc_port: int = Field(default=50051, env="CHROMA_SERVER_GRPC_PORT")
    chroma_server_cors_allow_origins: Union[str, List[str]] = Field(
        default="http://localhost:3000",
        env="CHROMA_SERVER_CORS_ALLOW_ORIGINS"
    )
    chroma_persist_directory: str = Field(default="./chroma_db", env="CHROMA_PERSIST_DIRECTORY")

    class Config:
        env_file_encoding = "utf-8"

    @field_validator("cors_origins", mode="before")
    def parse_cors_origins(cls, v):
        try:
            if isinstance(v, str):
                if v.startswith("[") and v.endswith("]"):
                    return json.loads(v)
                return [origin.strip() for origin in v.split(",") if origin.strip()]
            return v or ["*"]
        except Exception as e:
            logger.warning(f"Failed to parse CORS_ORIGINS: {v} ({e})")
            return ["*"]

    @field_validator("chroma_server_cors_allow_origins", mode="before")
    def parse_chroma_cors_origins(cls, v):
        try:
            if isinstance(v, str):
                if v.startswith("[") and v.endswith("]"):
                    return json.loads(v)
                return [origin.strip() for origin in v.split(",") if origin.strip()]
            return v or ["http://localhost:3000"]
        except Exception as e:
            logger.warning(f"Failed to parse CHROMA_SERVER_CORS_ALLOW_ORIGINS: {v} ({e})")
            return ["http://localhost:3000"]

    @field_validator("port")
    def validate_port(cls, v):
        if not (1 <= v <= 65535):
            raise ValueError("PORT must be between 1 and 65535")
        return v

    @field_validator("chroma_server_http_port")
    def validate_chroma_http_port(cls, v):
        if not (1 <= v <= 65535):
            raise ValueError("CHROMA_SERVER_HTTP_PORT must be between 1 and 65535")
        return v

    @field_validator("chroma_server_grpc_port")
    def validate_chroma_grpc_port(cls, v):
        if not (1 <= v <= 65535):
            raise ValueError("CHROMA_SERVER_GRPC_PORT must be between 1 and 65535")
        return v

settings = Settings()

# Debug output to verify Chroma settings
logger.info(f"Loaded config for {settings.app_name} v{settings.version}")
logger.info(f"Chroma CORS origins: {settings.chroma_server_cors_allow_origins}")
logger.info(f"Chroma HTTP port: {settings.chroma_server_http_port}")
logger.info(f"Chroma gRPC port: {settings.chroma_server_grpc_port}")

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
