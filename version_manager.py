import json
import os

def save_version(schema):
    file = "schema_versions.json"

    # Load existing versions
    if os.path.exists(file):
        with open(file, "r") as f:
            versions = json.load(f)
    else:
        versions = []

    # Extract only keys (important fix)
    current_keys = sorted(list(schema.keys()))

    if versions:
        last_keys = sorted(list(versions[-1].keys()))

        # ✅ Compare only keys
        if current_keys == last_keys:
            return  # skip duplicate

    # Save new version
    versions.append(schema.copy())

    with open(file, "w") as f:
        json.dump(versions, f, indent=4)