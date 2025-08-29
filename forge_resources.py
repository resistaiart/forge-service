# forge_resources.py
import re
import logging
from typing import Dict, List, Optional, Any, Callable, Tuple
from enum import Enum

# Set up logging
logger = logging.getLogger(__name__)

# Enums for consistent values
class ResourceType(Enum):
    MODEL = "model"
    DATASET = "dataset"
    LORA = "lora"
    EMBEDDING = "embedding"
    CHECKPOINT = "checkpoint"
    CODE = "code"
    SCRIPT = "script"
    UNKNOWN = "unknown"

class ResourceStatus(Enum):
    VERIFIED = "Verified"
    STALE = "Stale"
    RESTRICTED = "Restricted"
    EXPERIMENTAL = "Experimental"
    DEPRECATED = "Deprecated"
    COMMUNITY = "Community"

class ResourceHealth(Enum):
    ACTIVE = "active"
    EXPERIMENTAL = "experimental"
    BETA = "beta"
    UNMAINTAINED = "unmaintained"
    ARCHIVED = "archived"

class LicenseType(Enum):
    CC_BY = "CC-BY"
    MIT = "MIT"
    APACHE = "Apache-2.0"
    GPL = "GPL-3.0"
    PROPRIETARY = "Proprietary"
    UNKNOWN = "Unknown"

# Default values
DEFAULT_VALUES = {
    "type": ResourceType.UNKNOWN.value,
    "name": "unnamed",
    "creator": "unknown",
    "license": LicenseType.CC_BY.value,
    "health": ResourceHealth.ACTIVE.value,
    "status": ResourceStatus.VERIFIED.value,
    "version": "1.0.0",
    "size": "unknown",
    "compatibility": ["SD1.5", "SDXL"]
}

# Resource type patterns for auto-detection
RESOURCE_PATTERNS = {
    ResourceType.MODEL: re.compile(r\.(safetensors|ckpt|pt|pth)$|model|checkpoint, re.IGNORECASE),
    ResourceType.LORA: re.compile(r\.(lora|lycoris)$|lora|lycoris, re.IGNORECASE),
    ResourceType.EMBEDDING: re.compile(r\.(pt|bin)$|embedding|textualinversion, re.IGNORECASE),
    ResourceType.DATASET: re.compile(r\.(zip|tar|jsonl|parquet)$|dataset|training data, re.IGNORECASE),
    ResourceType.CODE: re.compile(r\.(py|js|json)$|code|script|implementation, re.IGNORECASE),
}

# Auto-tagging rules
AUTO_TAGGING_RULES = [
    # Status rules
    ("status", ResourceStatus.STALE.value, lambda r: any(x in r["name"].lower() for x in ["old", "legacy", "v1", "v2"])),
    ("status", ResourceStatus.RESTRICTED.value, lambda r: any(x in r["name"].lower() for x in ["nsfw", "adult", "explicit", "mature"])),
    ("status", ResourceStatus.EXPERIMENTAL.value, lambda r: any(x in r["name"].lower() for x in ["exp", "test", "wip"])),
    ("status", ResourceStatus.DEPRECATED.value, lambda r: any(x in r["name"].lower() for x in ["deprecated", "obsolete"])),
    ("status", ResourceStatus.COMMUNITY.value, lambda r: any(x in r["name"].lower() for x in ["community", "unofficial"])),
    
    # Health rules
    ("health", ResourceHealth.BETA.value, lambda r: "beta" in r["name"].lower()),
    ("health", ResourceHealth.EXPERIMENTAL.value, lambda r: any(x in r["name"].lower() for x in ["alpha", "experimental"])),
    ("health", ResourceHealth.UNMAINTAINED.value, lambda r: any(x in r["name"].lower() for x in ["abandoned", "unmaintained"])),
    ("health", ResourceHealth.ARCHIVED.value, lambda r: "archive" in r["name"].lower()),
    
    # License detection
    ("license", LicenseType.MIT.value, lambda r: "mit" in r["name"].lower() or "mit" in str(r.get("license", "")).lower()),
    ("license", LicenseType.APACHE.value, lambda r: "apache" in r["name"].lower() or "apache" in str(r.get("license", "")).lower()),
    ("license", LicenseType.GPL.value, lambda r: "gpl" in r["name"].lower() or "gpl" in str(r.get("license", "")).lower()),
]

def validate_resources(resources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Validates and annotates a list of resources with comprehensive metadata.
    Applies auto-tagging rules and type detection based on resource names and patterns.

    Args:
        resources: A list of resource dictionaries to process.

    Returns:
        A new list of annotated resource dictionaries with consistent metadata.

    Raises:
        ValueError: If resources is not a list or contains invalid items.
    """
    if not isinstance(resources, list):
        raise ValueError("Resources must be provided as a list")
    
    validated_resources = []
    
    for i, resource_input in enumerate(resources):
        try:
            if not isinstance(resource_input, dict):
                logger.warning(f"Skipping invalid resource at index {i}: not a dictionary")
                continue
                
            # Create a new resource with defaults
            resource = DEFAULT_VALUES.copy()
            resource.update(resource_input)  # User-provided values override defaults
            
            # Auto-detect resource type if not specified
            if resource["type"] == ResourceType.UNKNOWN.value:
                detected_type = _detect_resource_type(resource["name"])
                if detected_type:
                    resource["type"] = detected_type.value
            
            # Apply all auto-tagging rules
            for tag_key, tag_value, condition in AUTO_TAGGING_RULES:
                if condition(resource):
                    resource[tag_key] = tag_value
            
            # Validate and normalize values
            resource = _validate_and_normalize_resource(resource)
            
            # Add resource ID for tracking
            resource["id"] = f"res_{i}_{hash(resource['name']) % 10000:04d}"
            
            validated_resources.append(resource)
            
        except Exception as e:
            logger.error(f"Failed to process resource at index {i}: {e}")
            # Continue processing other resources even if one fails
    
    logger.info(f"Validated {len(validated_resources)} resources")
    return validated_resources

def _detect_resource_type(name: str) -> Optional[ResourceType]:
    """Attempt to detect resource type based on name patterns."""
    if not name:
        return None
        
    for resource_type, pattern in RESOURCE_PATTERNS.items():
        if pattern.search(name):
            return resource_type
    
    return None

def _validate_and_normalize_resource(resource: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and normalize resource fields."""
    resource = resource.copy()
    
    # Ensure type is valid
    if resource["type"] not in [t.value for t in ResourceType]:
        resource["type"] = ResourceType.UNKNOWN.value
    
    # Ensure status is valid
    if resource["status"] not in [s.value for s in ResourceStatus]:
        resource["status"] = ResourceStatus.VERIFIED.value
    
    # Ensure health is valid
    if resource["health"] not in [h.value for h in ResourceHealth]:
        resource["health"] = ResourceHealth.ACTIVE.value
    
    # Ensure license is valid
    if resource["license"] not in [l.value for l in LicenseType]:
        resource["license"] = LicenseType.UNKNOWN.value
    
    # Normalize name - remove extra spaces and special characters
    if "name" in resource:
        resource["name"] = re.sub(r'\s+', ' ', resource["name"]).strip()
    
    # Add timestamp
    resource["validated_at"] = "2024-01-01T00:00:00Z"  # Should use actual timestamp
    
    return resource

def filter_resources(resources: List[Dict[str, Any]], **filters) -> List[Dict[str, Any]]:
    """
    Filter resources based on criteria.
    
    Args:
        resources: List of resources to filter
        **filters: Key-value pairs to filter by (e.g., type="model", status="Verified")
    
    Returns:
        Filtered list of resources
    """
    filtered = resources.copy()
    
    for key, value in filters.items():
        if value is not None:
            filtered = [r for r in filtered if r.get(key) == value]
    
    return filtered

def get_resource_stats(resources: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Get statistics about a list of resources."""
    stats = {
        "total": len(resources),
        "by_type": {},
        "by_status": {},
        "by_health": {},
        "by_license": {}
    }
    
    for resource in resources:
        # Count by type
        stats["by_type"][resource["type"]] = stats["by_type"].get(resource["type"], 0) + 1
        
        # Count by status
        stats["by_status"][resource["status"]] = stats["by_status"].get(resource["status"], 0) + 1
        
        # Count by health
        stats["by_health"][resource["health"]] = stats["by_health"].get(resource["health"], 0) + 1
        
        # Count by license
        stats["by_license"][resource["license"]] = stats["by_license"].get(resource["license"], 0) + 1
    
    return stats

# --- Future expansion stubs ---
def _fetch_external_metadata(resource: Dict[str, Any]) -> Dict[str, Any]:
    """
    (Placeholder) Fetches real metadata from external sources.
    """
    # Implementation would call Hugging Face, CivitAI, GitHub APIs, etc.
    return resource

def validate_single_resource(resource: Dict[str, Any]) -> Dict[str, Any]:
    """Validate a single resource (convenience wrapper)."""
    return validate_resources([resource])[0]

# --- Example usage ---
if __name__ == "__main__":
    # Test with sample data
    sample_resources = [
        {"name": "Old Viking Model", "type": "model", "creator": "Alice"},
        {"name": "NSFW Fantasy Art Pack", "type": "dataset", "creator": "Bob"},
        {"name": "Beta Pipeline Code", "type": "code"},
        {"name": "Landscape Photos", "type": "dataset", "license": "MIT"},
        {"name": "cyberpunk-style-lora.safetensors", "creator": "AI Artist"},
        {"name": "experimental_embedding.pt", "creator": "Researcher"},
        {"name": "community-created-checkpoint.ckpt", "creator": "Community"}
    ]

    print("=== Original Resources ===")
    for item in sample_resources:
        print(f"  {item}")

    print("\n=== Validated Resources ===")
    result = validate_resources(sample_resources)
    for item in result:
        print(f"  {item}")

    print("\n=== Resource Statistics ===")
    stats = get_resource_stats(result)
    for category, counts in stats.items():
        if isinstance(counts, dict):
            print(f"  {category}:")
            for key, count in counts.items():
                print(f"    {key}: {count}")
        else:
            print(f"  {category}: {counts}")

    print("\n=== Filtered (Models Only) ===")
    models_only = filter_resources(result, type="model")
    for item in models_only:
        print(f"  {item}")
