# forge/resources.py
import re
import logging
import uuid
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


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


DEFAULT_VALUES = {
    "type": ResourceType.UNKNOWN.value,
    "name": "unnamed",
    "creator": "unknown",
    "license": LicenseType.CC_BY.value,
    "health": ResourceHealth.ACTIVE.value,
    "status": ResourceStatus.VERIFIED.value,
    "version": "1.0.0",
    "size": "unknown",
    "compatibility": ["SD1.5", "SDXL"],
}


RESOURCE_PATTERNS = {
    ResourceType.MODEL: re.compile(r"\.(safetensors|ckpt|pt|pth)$|model|checkpoint", re.IGNORECASE),
    ResourceType.LORA: re.compile(r"(lora|lycoris)|\.(safetensors|lora|lycoris)$", re.IGNORECASE),
    ResourceType.EMBEDDING: re.compile(r"\.(pt|bin|embedding)$|embedding|textualinversion", re.IGNORECASE),
    ResourceType.DATASET: re.compile(r"\.(zip|tar|jsonl|parquet)$|dataset|training\s?data", re.IGNORECASE),
    ResourceType.CODE: re.compile(r"\.(py|js|ipynb)$|script|implementation", re.IGNORECASE),
}


AUTO_TAGGING_RULES = [
    ("status", ResourceStatus.STALE.value, lambda r: any(x in r["name"].lower() for x in ["old", "legacy", "v1", "v2"])),
    ("status", ResourceStatus.RESTRICTED.value, lambda r: any(x in r["name"].lower() for x in ["nsfw", "adult", "explicit", "mature"])),
    ("status", ResourceStatus.EXPERIMENTAL.value, lambda r: any(x in r["name"].lower() for x in ["exp", "test", "wip"])),
    ("status", ResourceStatus.DEPRECATED.value, lambda r: any(x in r["name"].lower() for x in ["deprecated", "obsolete"])),
    ("status", ResourceStatus.COMMUNITY.value, lambda r: "community" in r["name"].lower()),

    ("health", ResourceHealth.BETA.value, lambda r: "beta" in r["name"].lower()),
    ("health", ResourceHealth.EXPERIMENTAL.value, lambda r: "experimental" in r["name"].lower()),
    ("health", ResourceHealth.UNMAINTAINED.value, lambda r: "unmaintained" in r["name"].lower()),
    ("health", ResourceHealth.ARCHIVED.value, lambda r: "archive" in r["name"].lower()),

    ("license", LicenseType.MIT.value, lambda r: "mit" in str(r.get("license", "")).lower()),
    ("license", LicenseType.APACHE.value, lambda r: "apache" in str(r.get("license", "")).lower()),
    ("license", LicenseType.GPL.value, lambda r: "gpl" in str(r.get("license", "")).lower()),
]


def validate_resources(resources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Validate and annotate resources with metadata."""
    if not isinstance(resources, list):
        raise ValueError("Resources must be provided as a list")

    validated_resources = []

    for i, resource_input in enumerate(resources):
        try:
            if not isinstance(resource_input, dict):
                logger.warning(f"Skipping invalid resource at index {i}: not a dict")
                continue

            resource = DEFAULT_VALUES.copy()
            resource.update(resource_input)

            if resource.get("type") == ResourceType.UNKNOWN.value:
                detected_type = _detect_resource_type(resource["name"])
                if detected_type:
                    resource["type"] = detected_type.value

            for tag_key, tag_value, condition in AUTO_TAGGING_RULES:
                # Only apply if not already explicitly set
                if condition(resource) and resource.get(tag_key) == DEFAULT_VALUES.get(tag_key):
                    resource[tag_key] = tag_value

            resource = _validate_and_normalize_resource(resource)

            # Stronger unique ID
            resource["id"] = f"res_{uuid.uuid4().hex[:8]}"

            validated_resources.append(resource)

        except Exception as e:
            logger.error(f"Failed to process resource at index {i}: {e}", exc_info=True)

    logger.info(f"Validated {len(validated_resources)} resources")
    return validated_resources


def _detect_resource_type(name: str) -> Optional[ResourceType]:
    if not name:
        return None
    for resource_type, pattern in RESOURCE_PATTERNS.items():
        if pattern.search(name):
            return resource_type
    return None


def _validate_and_normalize_resource(resource: Dict[str, Any]) -> Dict[str, Any]:
    resource = resource.copy()

    if resource["type"] not in [t.value for t in ResourceType]:
        resource["type"] = ResourceType.UNKNOWN.value
    if resource["status"] not in [s.value for s in ResourceStatus]:
        resource["status"] = ResourceStatus.VERIFIED.value
    if resource["health"] not in [h.value for h in ResourceHealth]:
        resource["health"] = ResourceHealth.ACTIVE.value
    if resource["license"] not in [l.value for l in LicenseType]:
        resource["license"] = LicenseType.UNKNOWN.value

    if "name" in resource:
        resource["name"] = re.sub(r"\s+", " ", str(resource["name"])).strip()

    resource["validated_at"] = datetime.now(timezone.utc).isoformat()
    return resource


def filter_resources(resources: List[Dict[str, Any]], **filters) -> List[Dict[str, Any]]:
    filtered = resources
    for key, value in filters.items():
        if value is not None:
            filtered = [r for r in filtered if r.get(key) == value]
    return filtered


def get_resource_stats(resources: List[Dict[str, Any]]) -> Dict[str, Any]:
    stats = {"total": len(resources), "by_type": {}, "by_status": {}, "by_health": {}, "by_license": {}}
    for r in resources:
        stats["by_type"][r["type"]] = stats["by_type"].get(r["type"], 0) + 1
        stats["by_status"][r["status"]] = stats["by_status"].get(r["status"], 0) + 1
        stats["by_health"][r["health"]] = stats["by_health"].get(r["health"], 0) + 1
        stats["by_license"][r["license"]] = stats["by_license"].get(r["license"], 0) + 1
    return stats


def validate_single_resource(resource: Dict[str, Any]) -> Dict[str, Any]:
    return validate_resources([resource])[0]


if __name__ == "__main__":
    sample_resources = [
        {"name": "Old Viking Model", "type": "model", "creator": "Alice"},
        {"name": "NSFW Fantasy Art Pack", "type": "dataset", "creator": "Bob"},
        {"name": "Beta Pipeline Code", "type": "code"},
        {"name": "Landscape Photos", "type": "dataset", "license": "MIT"},
        {"name": "cyberpunk-style-lora.safetensors", "creator": "AI Artist"},
        {"name": "experimental_embedding.pt", "creator": "Researcher"},
        {"name": "community-created-checkpoint.ckpt", "creator": "Community"},
    ]

    print("=== Validated Resources ===")
    result = validate_resources(sample_resources)
    for item in result:
        print(item)

    print("\n=== Resource Statistics ===")
    print(get_resource_stats(result))
