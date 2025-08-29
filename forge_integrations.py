```python
# forge_integrations.py
import os
import requests
from typing import Dict, List, Optional, Any
from enum import Enum

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
        self.config = {}
        
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
            "base_url": self.base_url
        }

# Specific Integration Implementations
class HuggingFaceIntegration(Integration):
    def __init__(self):
        super().__init__(
            name="huggingface",
            status=IntegrationStatus.ACTIVE,
            base_url="https://api-inference.huggingface.co"
        )
        
    def test_connection(self) -> bool:
        """Test HF connection by checking token validity."""
        if not self.config.get("api_token"):
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.config['api_token']}"}
            response = requests.get(f"{self.base_url}/models", headers=headers, timeout=10)
            return response.status_code == 200
        except:
            return False
            
    def query_model(self, model_id: str, payload: dict) -> Any:
        """Query a HF model."""
        headers = {"Authorization": f"Bearer {self.config.get('api_token', '')}"}
        response = requests.post(
            f"{self.base_url}/models/{model_id}",
            headers=headers,
            json=payload,
            timeout=30
        )
        return response.json()

class CivitAIIntegration(Integration):
    def __init__(self):
        super().__init__(
            name="civitai",
            status=IntegrationStatus.AVAILABLE,
            base_url="https://civitai.com/api/v1"
        )
        
    def test_connection(self) -> bool:
        """CivitAI doesn't require auth for basic queries."""
        try:
            response = requests.get(f"{self.base_url}/models", timeout=10)
            return response.status_code == 200
        except:
            return False
            
    def search_models(self, query: str, limit: int = 10) -> List[Dict]:
        """Search for models on CivitAI."""
        try:
            params = {"query": query, "limit": limit}
            response = requests.get(f"{self.base_url}/models", params=params, timeout=15)
            return response.json().get("items", [])
        except Exception as e:
            print(f"CivitAI search failed: {e}")
            return []

class ComfyUIConnectionIntegration(Integration):
    def __init__(self):
        super().__init__(
            name="comfyui-connect",
            status=IntegrationStatus.PLANNED,
            base_url=None
        )
        
    def test_connection(self) -> bool:
        # TODO: Implement ComfyUI API connection test
        return False

# Integration Registry
class IntegrationManager:
    """Manage all integrations."""
    
    def __init__(self):
        self.integrations: Dict[str, Integration] = {}
        self._initialize_integrations()
        
    def _initialize_integrations(self):
        """Initialize all available integrations."""
        self.register(HuggingFaceIntegration())
        self.register(CivitAIIntegration())
        self.register(ComfyUIConnectionIntegration())
        
        # Add more integrations as they are created
        self.register(Integration("arxiv", IntegrationStatus.PLANNED, "https://arxiv.org"))
        self.register(Integration("reddit", IntegrationStatus.PLANNED, "https://www.reddit.com"))
        self.register(Integration("x-platform", IntegrationStatus.PLANNED, "https://api.x.com"))
        
    def register(self, integration: Integration):
        """Register a new integration."""
        self.integrations[integration.name] = integration
        
    def get(self, name: str) -> Optional[Integration]:
        """Get a specific integration."""
        return self.integrations.get(name)
        
    def list_integrations(self, active_only: bool = True) -> Dict[str, Dict]:
        """List all integrations with their status."""
        result = {}
        for name, integration in self.integrations.items():
            status = integration.get_status()
            if active_only and status["status"] not in ["active", "available"]:
                continue
            result[name] = status
        return result
        
    def configure_integration(self, name: str, **kwargs) -> bool:
        """Configure an integration."""
        integration = self.get(name)
        if integration:
            integration.configure(**kwargs)
            
            # Test connection after configuration
            if integration.test_connection():
                integration.status = IntegrationStatus.ACTIVE
            else:
                integration.status = IntegrationStatus.ERROR
                
            return integration.status == IntegrationStatus.ACTIVE
        return False

# Global instance
integration_manager = IntegrationManager()

# Original function for backward compatibility
def list_integrations(active_only: bool = True) -> Dict[str, Dict]:
    """
    List ecosystem integrations.
    """
    return integration_manager.list_integrations(active_only)

# Utility functions
def get_huggingface_client() -> Optional[HuggingFaceIntegration]:
    """Get configured HuggingFace client."""
    hf = integration_manager.get("huggingface")
    if hf and hf.status == IntegrationStatus.ACTIVE:
        return hf
    return None

def get_civitai_client() -> Optional[CivitAIIntegration]:
    """Get CivitAI client."""
    civitai = integration_manager.get("civitai")
    if civitai and civitai.status in [IntegrationStatus.ACTIVE, IntegrationStatus.AVAILABLE]:
        return civitai
    return None
```

### Usage Examples

```python
# Initialize and configure integrations
from forge_integrations import integration_manager, get_huggingface_client

# Configure HuggingFace with API token
integration_manager.configure_integration(
    "huggingface",
    api_token=os.getenv("HF_TOKEN")
)

# List active integrations
active_integrations = integration_manager.list_integrations(active_only=True)
print("Active integrations:", active_integrations)

# Use HuggingFace integration
hf_client = get_huggingface_client()
if hf_client:
    result = hf_client.query_model(
        "nlpconnect/vit-gpt2-image-captioning",
        {"inputs": "https://example.com/image.jpg"}
    )
    print("HF Result:", result)

# Use CivitAI integration
civitai = integration_manager.get("civitai")
if civitai:
    models = civitai.search_models("cyberpunk", limit=5)
    print("Found models:", models)
```
