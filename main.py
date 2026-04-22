import json
import pandas as pd

from schema_engine import *
from version_manager import *
from logger import *

final_data = []
confidence_list = []
drift_detected = False

with open("data.json") as f:
    for line in f:
        data = json.loads(line)
        print("\nIncoming:", data)

        schema, changes = update_schema(data)

        if changes:
            save_version(schema)
            for c in changes:
                log_change(c)
                print("Change:", c)

        if detect_drift(data):
            drift_detected = True
            print("⚠️ Drift detected")

        missing = detect_missing_fields(data)
        if missing:
            print("Missing fields:", missing)

        clean = standardize(data)
        final_data.append(clean)

        score = confidence_score(data)
        confidence_list.append(score)
        print("Confidence:", score)

df = pd.DataFrame(final_data)
df.to_csv("output.csv", index=False)

print("\n📊 Records:", len(df))
print("📊 Avg Confidence:", round(sum(confidence_list)/len(confidence_list), 2))
print("🔮 Predicted Field:", predict_next_field())
print("⚠️ Drift:", drift_detected)

print("\n✅ Output saved to output.csv")