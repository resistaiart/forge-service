# forge_resources.py

# 1. Define constants for consistent values (easy to update in one place)
DEFAULT_VALUES = {
    "type": "unknown",
    "name": "unnamed",
    "creator": "unknown",
    "license": "CC-BY",
    "health": "active",
    "status": "Verified"
}

# 2. Define rules for auto-tagging. This is more scalable than if/else blocks.
# Format: (key_to_set, value_to_set, condition_lambda)
AUTO_TAGGING_RULES = [
    ("status", "Stale", lambda r: "old" in r["name"].lower() or "legacy" in r["name"].lower()),
    ("status", "Restricted", lambda r: any(x in r["name"].lower() for x in ["nsfw", "adult", "explicit"])),
    ("health", "experimental", lambda r: "beta" in r["name"].lower() or "test" in r["name"].lower()),
]

def validate_resources(resources):
    """
    Validates and annotates a list of resources with type, creator, license, status, and health.
    Applies simple auto-tagging rules based on resource names. This function is designed to be
    extended with real metadata fetching from external sources in the future.

    Args:
        resources (list[dict]): A list of resource dictionaries to process.

    Returns:
        list[dict]: A new list of annotated resource dictionaries.
    """
    validated_resources = []

    for resource_input in resources:
        # 1. Create a new resource dict with defaults
        resource = {}
        for key, default_value in DEFAULT_VALUES.items():
            resource[key] = resource_input.get(key, default_value)

        # 2. (Future Hook) Add basic validation logic here.
        #    For example, you could check if 'type' is in an allowed list.
        #    if resource["type"] not in ["model", "dataset", "code"]:
        #        resource["type"] = "unknown"

        # 3. Apply all auto-tagging rules
        for tag_key, tag_value, condition in AUTO_TAGGING_RULES:
            if condition(resource):
                resource[tag_key] = tag_value

        # 4. (Future Hook) Placeholder for fetching real metadata.
        #    This could call an API or a database.
        #    resource = _fetch_external_metadata(resource)

        validated_resources.append(resource)

    return validated_resources


# --- Stub function for future expansion ---
def _fetch_external_metadata(resource):
    """
    (Placeholder) Fetches real metadata from an external source like Hugging Face,
    CivitAI, or GitHub based on the resource's name or ID.

    Args:
        resource (dict): The resource dictionary to enrich.

    Returns:
        dict: The enriched resource dictionary.
    """
    # Example future logic:
    # if resource["type"] == "model":
    #    # Make an API call to get download counts, likes, etc.
    #    api_data = _call_huggingface_api(resource["name"])
    #    resource["downloads"] = api_data.get("downloads")
    #    resource["last_updated"] = api_data.get("lastUpdated")
    return resource


# --- Example usage ---
if __name__ == "__main__":
    # Test with some example data
    sample_resources = [
        {"name": "Old Viking Model", "type": "model", "creator": "Alice"},
        {"name": "NSFW Fantasy Art Pack", "type": "dataset", "creator": "Bob"},
        {"name": "Beta Pipeline Code", "type": "code"}, # Tests defaults
        {"name": "Landscape Photos", "type": "dataset", "license": "MIT"} # Tests keeping good license
    ]

    result = validate_resources(sample_resources)

    # Print the results
    for item in result:
        print(item)
