import streamlit as st
import pandas as pd
import uuid
import re
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
import plotly.graph_objects as go

# === 1. Load CSV File ===
df = pd.read_csv("lemans_200_data_with_pes.csv")

# === 2. Embedding Model ===
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")  # 384-dim

def get_embedding(text):
    return embedding_model.encode(text, convert_to_numpy=True).tolist()

# === 3. Qdrant Setup ===
qdrant = QdrantClient(
    host="localhost",
    port=6333
)

collection_name = "lemans_data"

if not qdrant.collection_exists(collection_name):
    qdrant.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE)
    )

    def row_to_text(row):
        return (
            f"Tire Pressure Front: {row['TirePressure_Front']} bar, "
            f"Tire Pressure Rear: {row['TirePressure_Rear']} bar, "
            f"Tire Size Front: {row['TireSize_Front']}, "
            f"Tire Size Rear: {row['TireSize_Rear']}, "
            f"Driver Weight: {row['DriverWeight_kg']} kg, "
            f"Coolant Temperature: {row['CoolantTemperature_C']} °C, "
            f"Coolant Type: {row['CoolantType']}, "
            f"PES: {row['PES']}"
        )

    points = []
    for _, row in df.iterrows():
        text = row_to_text(row)
        vector = get_embedding(text)
        points.append(PointStruct(id=str(uuid.uuid4()), vector=vector, payload={"text": text}))
    qdrant.upsert(collection_name=collection_name, points=points)

# === 4. Utility Functions ===
def sanitize_input(text):
    return re.sub(r"[^\w\s\-.,?]", "", text)[:300]

def search_similar_texts(query, top_k=5):
    query_vector = get_embedding(query)
    results = qdrant.search(
        collection_name=collection_name,
        query_vector=query_vector,
        limit=top_k,
        with_payload=True
    )
    return [r.payload["text"] for r in results]

def parse_row(text):
    def extract(pattern):
        match = re.search(pattern, text)
        return float(match.group(1)) if match else None

    return {
        "TirePressure_Front": extract(r"Tire Pressure Front: ([\d.]+)"),
        "TirePressure_Rear": extract(r"Tire Pressure Rear: ([\d.]+)"),
        "TireSize_Front": extract(r"Tire Size Front: ([\d.]+)"),
        "TireSize_Rear": extract(r"Tire Size Rear: ([\d.]+)"),
        "DriverWeight_kg": extract(r"Driver Weight: ([\d.]+)"),
        "CoolantTemperature_C": extract(r"Coolant Temperature: ([\d.]+)"),
        "PES": extract(r"PES: ([\d.eE+-]+)")
    }

def compute_pes(row):
    try:
        avg_tire_size = (row["TireSize_Front"] + row["TireSize_Rear"]) / 2
        avg_pressure = (row["TirePressure_Front"] + row["TirePressure_Rear"]) / 2
        return (1 / (row["CoolantTemperature_C"] * row["DriverWeight_kg"] * avg_tire_size)) * (1 + avg_pressure / 30)
    except:
        return 0

def estimate_lap_time(pes):
    return 180 - (pes * 100000)  # basic approximation

def calculate_distance_and_speed(lap_time_sec):
    distance_km = 13.626  # Le Mans circuit length
    avg_speed_kph = (distance_km / (lap_time_sec / 3600))
    return distance_km, avg_speed_kph

def suggest_adjustments(row):
    suggestions = []

    def format_range(value, min_val, max_val, label, unit, emoji):
        if value < min_val:
            return f"{emoji} {label} is too low ({value}{unit}). Increase to {min_val}–{max_val}{unit}."
        elif value > max_val:
            return f"{emoji} {label} is too high ({value}{unit}). Reduce to {min_val}–{max_val}{unit}."
        else:
            return f"✅ {label} is optimal at {value}{unit} (within {min_val}–{max_val}{unit})."

    suggestions.append(format_range(row["CoolantTemperature_C"], 85, 95, "Coolant Temperature", "°C", "🌡️"))
    suggestions.append(format_range(row["DriverWeight_kg"], 68, 72, "Driver Weight", "kg", "⚖️"))

    front = row["TireSize_Front"]
    rear = row["TireSize_Rear"]
    if front != 305 or rear != 305:
        suggestions.append(f"🚞 Use 305 mm tire size for both front and rear (currently {front}/{rear}) for optimal PES.")
    else:
        suggestions.append("✅ Tire sizes are optimal at 305 mm (front and rear).")

    avg_pressure = (row["TirePressure_Front"] + row["TirePressure_Rear"]) / 2
    suggestions.append(format_range(avg_pressure, 21.5, 22.5, "Average Tire Pressure", " PSI", "🔧"))

    return suggestions

def rag_query_pipeline(query):
    context_passages = search_similar_texts(query)
    parsed = parse_row(context_passages[0])
    pes = compute_pes(parsed)
    suggestions = suggest_adjustments(parsed)
    lap_time = estimate_lap_time(pes)
    distance, speed = calculate_distance_and_speed(lap_time)

    return {
        "context": context_passages[0],
        "row": parsed,
        "pes": pes,
        "lap_time": lap_time,
        "distance": distance,
        "speed": speed,
        "suggestions": suggestions
    }

# === 5. Streamlit UI ===
st.set_page_config(page_title="PES Advisor", page_icon="🏍️")
st.title("🏎️ LeMans PES Performance Advisor")

# --- RAG Query ---
query = sanitize_input(st.text_input("Ask a question about improving PES performance:", value="How to improve PES?"))

if st.button("Analyze from history"):
    result = rag_query_pipeline(query)
    st.subheader("📌 Closest Match")
    st.code(result["context"])

    st.subheader("📈 Estimated PES")
    st.success(f"{result['pes']:.6f}")

    st.subheader("🏎️ Estimated Lap Time")
    st.info(f"{result['lap_time']:.2f} seconds")

    st.subheader("📏 Distance Covered")
    st.info(f"{result['distance']:.3f} km")

    st.subheader("🚀 Average Speed")
    st.info(f"{result['speed']:.2f} km/h")

    st.subheader("🛠️ Suggestions")
    for s in result['suggestions']:
        st.markdown(f"- {s}")

# --- Manual Input ---
st.markdown("---")
st.header("📋 Manual Input")

with st.form("manual_form"):
    col1, col2 = st.columns(2)
    with col1:
        tire_pressure_front = st.number_input("Tire Pressure Front (PSI)", value=22.0)
        tire_size_front = st.number_input("Tire Size Front (mm)", value=305.0)
        driver_weight = st.number_input("Driver Weight (kg)", value=70.0)
    with col2:
        tire_pressure_rear = st.number_input("Tire Pressure Rear (PSI)", value=22.0)
        tire_size_rear = st.number_input("Tire Size Rear (mm)", value=305.0)
        coolant_temp = st.number_input("Coolant Temperature (°C)", value=90.0)

    submitted = st.form_submit_button("Analyze Custom")

if submitted:
    row = {
        "TirePressure_Front": tire_pressure_front,
        "TirePressure_Rear": tire_pressure_rear,
        "TireSize_Front": tire_size_front,
        "TireSize_Rear": tire_size_rear,
        "DriverWeight_kg": driver_weight,
        "CoolantTemperature_C": coolant_temp
    }
    pes = compute_pes(row)
    lap_time = estimate_lap_time(pes)
    distance, speed = calculate_distance_and_speed(lap_time)
    suggestions = suggest_adjustments(row)

    st.subheader("📈 Estimated PES")
    st.success(f"{pes:.6f}")

    st.subheader("🏎️ Estimated Lap Time")
    st.info(f"{lap_time:.2f} seconds")

    st.subheader("📏 Distance Covered")
    st.info(f"{distance:.3f} km")

    st.subheader("🚀 Average Speed")
    st.info(f"{speed:.2f} km/h")

    st.subheader("🛠️ Suggestions")
    for s in suggestions:
        st.markdown(f"- {s}")

    st.subheader("📉 Comparison Radar Chart")
    labels = ["Coolant Temp", "Driver Weight", "Tire Size", "Tire Pressure", "PES"]
    user_vals = [coolant_temp, driver_weight, (tire_size_front + tire_size_rear)/2, (tire_pressure_front + tire_pressure_rear)/2, pes]
    ideal_vals = [90, 70, 305, 22, 0.001]
    user_norm = [(v - minv) / (maxv - minv) for v, minv, maxv in zip(user_vals, [80, 60, 295, 20, 0], [100, 80, 315, 25, 0.0015])]
    ideal_norm = [(v - minv) / (maxv - minv) for v, minv, maxv in zip(ideal_vals, [80, 60, 295, 20, 0], [100, 80, 315, 25, 0.0015])]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=user_norm, theta=labels, fill='toself', name='User'))
    fig.add_trace(go.Scatterpolar(r=ideal_norm, theta=labels, fill='toself', name='Ideal'))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 1])), showlegend=True)
    st.plotly_chart(fig, use_container_width=True)

    lap_time_ideal = estimate_lap_time(0.001)
    delta = lap_time - lap_time_ideal
    st.subheader("⏱️ Lap Time Delta")
    st.info(f"Your current parameters result in +{delta:.2f} seconds slower than ideal.")
