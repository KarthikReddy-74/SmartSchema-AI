master_schema = {}

# NEW: tracking for importance
field_total_count = {}
field_valid_count = {}

# Keep this if you already use prediction
field_frequency = {}

def detect_type(value):
    if value is None:
        return "null"
    try:
        int(value)
        return "int"
    except:
        try:
            float(value)
            return "float"
        except:
            return "str"


def process_record(record):
    changes = []
    cleaned = {}
    confidence = 1.0
    reason = []

    for key, value in record.items():

        detected_type = detect_type(value)

        # New field
        if key not in master_schema:
            master_schema[key] = detected_type
            changes.append(f"Added field: {key}")

        # Type change
        elif master_schema[key] != detected_type and value is not None:
            changes.append(f"Type changed: {key}")
            master_schema[key] = detected_type
            confidence -= 0.2
            reason.append("Invalid type")

        # Missing value
        if value is None:
            confidence -= 0.2
            reason.append("Missing value")

        # ✅ Field importance tracking
        field_total_count[key] = field_total_count.get(key, 0) + 1

        if value is not None:
            field_valid_count[key] = field_valid_count.get(key, 0) + 1

        # Prediction tracking
        field_frequency[key] = field_frequency.get(key, 0) + 1

        cleaned[key] = value

    return cleaned, changes, max(confidence, 0.1), list(set(reason))


# ✅ NEW FUNCTION
def get_field_importance():
    importance = {}

    for key in field_total_count:
        valid = field_valid_count.get(key, 0)
        total = field_total_count.get(key, 1)

        importance[key] = round(valid / total, 2)

    return importance