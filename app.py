import streamlit as st
import json
import pandas as pd

from schema_engine import process_record, get_field_importance
from schema_engine import master_schema, field_total_count, field_valid_count, field_frequency

st.set_page_config(page_title="SmartSchemaAI", layout="wide")

st.title("🚀 SmartSchemaAI - Intelligent Schema Evolution System")

# -------------------------------
# RESET WHEN NEW FILE UPLOADED
# -------------------------------
if "last_file" not in st.session_state:
    st.session_state.last_file = None

uploaded_file = st.file_uploader("Upload JSON or CSV file", type=["json", "csv"])

if uploaded_file is not None:

    # Reset schema if new file
    if st.session_state.last_file != uploaded_file.name:
        master_schema.clear()
        field_total_count.clear()
        field_valid_count.clear()
        field_frequency.clear()

        st.session_state.last_file = uploaded_file.name
        st.success("✅ New dataset detected → Schema reset done!")

    # -------------------------------
    # READ FILE (JSON / CSV)
    # -------------------------------
    try:
        if uploaded_file.name.endswith(".json"):
            data = json.load(uploaded_file)

        elif uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file, encoding="utf-8")
            df = df.where(pd.notnull(df), None)  # convert NaN → None
            data = df.to_dict(orient="records")

    except Exception as e:
        st.error(f"File reading error: {e}")
        st.stop()

    # -------------------------------
    # PROCESS DATA
    # -------------------------------
    st.subheader("📥 Incoming Data")

    all_cleaned = []
    all_confidence = []
    drift_detected = False

    for record in data:

        st.json(record)

        clean, changes, confidence, reason = process_record(record)

        # Show changes
        for c in changes:
            st.success(c)

        # Detect missing fields (ONLY current dataset)
        missing = [k for k, v in record.items() if v is None]
        if missing:
            st.error(f"⚠ Missing fields: {missing}")

        # Drift detection
        if confidence < 0.5:
            drift_detected = True

        st.info(f"Confidence: {round(confidence,2)}, Reason: {reason}")

        all_cleaned.append(clean)
        all_confidence.append(confidence)

    # -------------------------------
    # METRICS
    # -------------------------------
    st.subheader("📊 Metrics")

    col1, col2, col3 = st.columns(3)

    col1.metric("Records", len(all_cleaned))
    col2.metric("Schema Fields", len(master_schema))
    col3.metric("Avg Confidence", round(sum(all_confidence)/len(all_confidence), 2))

    # -------------------------------
    # CLEANED DATA
    # -------------------------------
    st.subheader("🧹 Cleaned Data")

    df_clean = pd.DataFrame(all_cleaned)
    df_clean = df_clean.where(pd.notnull(df_clean), None)

    st.dataframe(df_clean)

    # -------------------------------
    # DRIFT DETECTION
    # -------------------------------
    st.subheader("⚠ Drift Detection")

    if drift_detected:
        st.error("🚨 Drift Detected (Low confidence records found)")
    else:
        st.success("✅ No Drift Detected")

    # -------------------------------
    # PREDICT NEXT FIELD
    # -------------------------------
    st.subheader("🔮 Predicted Next Field")

    if field_frequency:
        predicted = max(field_frequency, key=field_frequency.get)
        st.success(f"📌 Predicted Field: {predicted}")

    # -------------------------------
    # CONFIDENCE TREND
    # -------------------------------
    st.subheader("📈 Confidence Trend")

    st.line_chart(all_confidence)

    # -------------------------------
    # FIELD IMPORTANCE (FIXED)
    # -------------------------------
    st.subheader("📊 Field Importance")

    importance = get_field_importance()
    st.bar_chart(importance)

    # -------------------------------
    # SCHEMA EVOLUTION TIMELINE
    # -------------------------------
    st.subheader("📜 Schema Evolution Timeline")

    displayed = set()
    version = 1

    for record in all_cleaned:
        fields = tuple(sorted(record.keys()))

        if fields not in displayed:
            st.write(f"Version {version}: {list(fields)}")
            displayed.add(fields)
            version += 1