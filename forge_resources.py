# forge_resources.py
def validate_resources(resources):
    """
    Validate checkpoints, LoRAs, embeddings.
    Right now: returns input with placeholder statuses.
    Later: real verification logic.
    """
    validated = []
    for r in resources:
        validated.append({
            "type": r.get("type", "unknown"),
            "name": r.get("name", "unnamed"),
            "status": r.get("status", "Verified")  # default placeholder
        })
    return validated
