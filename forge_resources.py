# forge_resources.py

def validate_resources(resources):
    """
    Annotate resources with type, creator, license, status.
    Stubbed now with placeholders — later can fetch real metadata.
    """
    validated = []
    for r in resources:
        resource = {
            "type": r.get("type", "unknown"),
            "name": r.get("name", "unnamed"),
            "creator": r.get("creator", "unknown"),
            "license": r.get("license", "CC-BY"),
            "health": r.get("health", "active"),
            "status": r.get("status", "Verified")
        }

        # Simple auto-tagging
        if "old" in resource["name"].lower():
            resource["status"] = "Stale"
        if "nsfw" in resource["name"].lower():
            resource["status"] = "Restricted"

        validated.append(resource)

    return validated
