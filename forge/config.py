import os
import logging
import json
from typing import List, Union
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator

# Load .env from the correct location if it exists
env_path = Path("forge-service") / ".env"
if env_path.exists():
    load_dotenv(env_path)
else:
    # For Railway/cloud deployment, .env might not exist
    load_dotenv()  # Load from environment variables only

logger = logging.getLogger(__name__)

# DEBUG: Check environment variables before loading settings
print("=== ENVIRONMENT VARIABLE DEBUG ===")
print(f"CORS_ORIGINS: '{os.getenv('CORS_ORIGINS')}'")
print(f"CHROMA_SERVER_CORS_ALLOW_ORIGINS: '{os.getenv('CHROMA_SERVER_CORS_ALLOW_ORIGINS')}'")
print(f"PORT: '{os.getenv('PORT')}'")
print("==================================")

class Settings(BaseSettings):
    app_name: str = "Forge API"
    version: str = "v2.0"
    environment: str = Field(default="production", env="ENV")
    debug: bool = Field(default=False, env="DEBUG")

    port: int = Field(default=8000, env="PORT")
    
    # Will be parsed from JSON string to list
    cors_origins: List[str] = Field(default=["*"])
    
    enable_legacy: bool = Field(default=True, env="FORGE_ENABLE_LEGACY")

    # Chroma DB Configuration
    chroma_server_host: str = Field(default="0.0.0.0", env="CHROMA_SERVER_HOST")
    chroma_server_http_port: int = Field(default=8000, env="CHROMA_SERVER_HTTP_PORT")
    chroma_server_grpc_port: int = Field(default=50051, env="CHROMA_SERVER_GRPC_PORT")
    chroma_server_cors_allow_origins: List[str] = Field(default=["http://localhost:3000"])
    chroma_persist_directory: str = Field(default="./chroma_db", env="CHROMA_PERSIST_DIRECTORY")

    class Config:
        env_file_encoding = "utf-8"
        case_sensitive = False

    @field_validator("cors_origins", mode="before")
    def parse_cors_origins(cls, v):
        """Parse CORS_ORIGINS from JSON string or comma-separated string"""
        if v is None:
            return ["*"]
        
        if isinstance(v, str):
            try:
                # Try to parse as JSON first
                if v.strip().startswith('[') and v.strip().endswith(']'):
                    return json.loads(v)
                # Fallback to comma-separated parsing
                if v.strip() == "*":
                    return ["*"]
                return [origin.strip() for origin in v.split(",") if origin.strip()]
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON in CORS_ORIGINS: {v}")
                return ["*"]
        return v

    @field_validator("chroma_server_cors_allow_origins", mode="before")
    def parse_chroma_cors_origins(cls, v):
        """Parse CHROMA_SERVER_CORS_ALLOW_ORIGINS from JSON string"""
        if v is None:
            return ["http://localhost:3000"]
        
        if isinstance(v, str):
            try:
                # Try to parse as JSON first
                if v.strip().startswith('[') and v.strip().endswith(']'):
                    return json.loads(v)
                # Fallback to comma-separated parsing
                if v.strip() == "*":
                    return ["*"]
                return [origin.strip() for origin in v.split(",") if origin.strip()]
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON in CHROMA_SERVER_CORS_ALLOW_ORIGINS: {v}")
                return ["http://localhost:3000"]
        return v

    @field_validator("port", "chroma_server_http_port", "chroma_server_grpc_port", mode="before")
    def validate_ports(cls, v):
        if isinstance(v, str):
            try:
                v = int(v)
            except ValueError:
                raise ValueError("Port must be a number")
        if not (1 <= v <= 65535):
            raise ValueError("Port must be between 1 and 65535")
        return v

# Create settings instance
try:
    settings = Settings()
    logger.info(f"✅ Successfully loaded config for {settings.app_name} v{settings.version}")
    logger.info(f"📍 Environment: {settings.environment}")
    logger.info(f"🌐 CORS origins: {settings.cors_origins}")
    logger.info(f"🔧 Chroma CORS: {settings.chroma_server_cors_allowed_origins}")
except Exception as e:
    logger.error(f"❌ Failed to load settings: {e}")
    # Fallback to basic settings
    import sys
    sys.exit(1)

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
