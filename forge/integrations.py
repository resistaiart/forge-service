import os
import requests
import logging
from typing import Dict, List, Optional, Any
from enum import Enum

logger = logging.getLogger(__name__)

class IntegrationStatus(Enum):
    ACTIVE = "active"
    AVAILABLE = "available"
    PLANNED = "planned"
    DISABLED = "disabled"
    ERROR = "error"

class Integration:
    """Base class for all integrations."""

    def __init__(self, name: str, status: IntegrationStatus, base_url: Optional[str] = None):
        self.name = name
        self.status = status
        self.base_url = base_url
        self.config: Dict[str, Any] = {}

    def configure(self, **kwargs):
        """Configure integration with API keys or settings."""
        self.config.update(kwargs)
        return self

    def test_connection(self) -> bool:
        """Test if integration is working."""
        raise NotImplementedError("Subclasses must implement test_connection")

    def get_status(self) -> Dict[str, Any]:
        """Get detailed status of integration."""
        return {
            "name": self.name,
            "status": self.status.value,
            "configured": bool(self.config),
            "base_url": self.base_url,
        }

class HuggingFaceIntegration(Integration):
    def __init__(self):
        super().__init__(
            name="huggingface",
            status=IntegrationStatus.AVAILABLE,
            base_url="https://api-inference.huggingface.co"
        )

    def test_connection(self) -> bool:
        if not self.config.get("api_token"):
            return False
        try:
            headers = {"Authorization": f"Bearer {self.config['api_token']}"}
            response = requests.get(f"{self.base_url}/models", headers=headers, timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"HuggingFace connection failed: {e}")
            return False

    def query_model(self, model_id: str, payload: dict) -> Any:
        headers = {"Authorization": f"Bearer {self.config.get('api_token', '')}"}
        response = requests.post(
            f"{self.base_url}/models/{model_id}",
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        return response.json()

class CivitAIIntegration(Integration):
    def __init__(self):
        super().__init__(
            name="civitai",
            status=IntegrationStatus.AVAILABLE,
            base_url="https://civitai.com/api/v1"
        )

    def test_connection(self) -> bool:
        try:
            response = requests.get(f"{self.base_url}/models", timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"CivitAI connection failed: {e}")
            return False

    def search_models(self, query: str, limit: int = 10) -> List[Dict]:
        try:
            params = {"query": query, "limit": limit}
            response = requests.get(f"{self.base_url}/models", params=params, timeout=15)
            response.raise_for_status()
            return response.json().get("items", [])
        except Exception as e:
            logger.error(f"CivitAI search failed: {str(e)}")
            return []

def list_integrations() -> List[str]:
    """List all available integrations."""
    integrations = [HuggingFaceIntegration(), CivitAIIntegration()]
    active_integrations = [
        integration.name for integration in integrations if integration.status == IntegrationStatus.ACTIVE
    ]
    return active_integrations
