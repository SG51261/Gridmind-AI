import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ----------- PAGE SETUP -----------
st.set_page_config(page_title="⚡ GridMind AI", layout="wide")

# ----------- DARK UI -----------
st.markdown("""
<style>
.stApp { background-color: #121212; color: white; }
.stButton>button { background-color: #00BFFF; color: white; }
h1, h2, h3 { color: #00BFFF; }
</style>
""", unsafe_allow_html=True)

TOTAL_CAPACITY = 1000

# ----------- SESSION STATE -----------
if "areas" not in st.session_state:
    st.session_state.areas = []
if "result_ready" not in st.session_state:
    st.session_state.result_ready = False

# ----------- SCENARIOS -----------
def load_scenario(level):
    if level == "Easy":
        return [
            {"name": "Hospital", "priority": "Critical", "current": 120},
            {"name": "City Center", "priority": "High", "current": 100},
            {"name": "Residential", "priority": "Low", "current": 80},
        ]
    elif level == "Medium":
        return [
            {"name": "Hospital", "priority": "Critical", "current": 150},
            {"name": "Data Center", "priority": "Critical", "current": 140},
            {"name": "Industry", "priority": "High", "current": 120},
            {"name": "City Center", "priority": "Medium", "current": 100},
            {"name": "Residential", "priority": "Low", "current": 90},
        ]
    else:
        return [
            {"name": "Hospital", "priority": "Critical", "current": 200},
            {"name": "Nuclear Plant", "priority": "Critical", "current": 220},
            {"name": "Data Center", "priority": "Critical", "current": 210},
            {"name": "Industry", "priority": "High", "current": 180},
            {"name": "City Center", "priority": "Medium", "current": 160},
            {"name": "Residential", "priority": "Low", "current": 140},
        ]

# ----------- HEADER -----------
st.title("⚡ GridMind AI")
st.subheader("Simple Smart Grid Dashboard")

# ----------- CONTROLS -----------
col1, col2 = st.columns(2)

scenario = col1.selectbox("Scenario", ["Easy", "Medium", "Hard"])
difficulty = col2.selectbox("Difficulty", ["Easy", "Medium", "Hard"])

# ----------- BUTTONS -----------
if st.button("Load Scenario"):
    st.session_state.areas = load_scenario(scenario)
    st.session_state.result_ready = False

if st.button("🚀 Run AI Simulation"):
    if not st.session_state.areas:
        st.warning("Please load a scenario first!")
    else:
        modifier = {"Easy": 0.05, "Medium": 0.1, "Hard": 0.2}[difficulty]

        areas = st.session_state.areas
        total_load = sum(a["current"] for a in areas)
        utilization = total_load / TOTAL_CAPACITY * 100

        for area in areas:
            predicted = area["current"] * np.random.uniform(1 - modifier, 1 + modifier)

            if predicted > area["current"]:
                if area["priority"] in ["Critical", "High"]:
                    allocated = predicted * 1.05
                    status = "Increase"
                else:
                    allocated = predicted
                    status = "Normal"
            else:
                if area["priority"] == "Low":
                    allocated = predicted * 0.9
                    status = "Reduce"
                else:
                    allocated = predicted
                    status = "Normal"

            if utilization > 90 and area["priority"] in ["Low", "Medium"]:
                allocated = 0
                status = "Cut"

            area["predicted"] = round(predicted, 1)
            area["allocated"] = round(allocated, 1)
            area["status"] = status

        st.session_state.result_ready = True

# ----------- DISPLAY RESULT SAFELY -----------
if st.session_state.result_ready:

    areas = st.session_state.areas
    total_load = sum(a["current"] for a in areas)
    utilization = total_load / TOTAL_CAPACITY * 100

    # ----------- METRICS -----------
    c1, c2, c3 = st.columns(3)
    c1.metric("Capacity", TOTAL_CAPACITY)
    c2.metric("Load", total_load)
    c3.metric("Utilization", f"{utilization:.1f}%")

    # ----------- STATUS -----------
    if utilization > 90:
        st.error("🚨 GRID OVERLOAD")
    else:
        st.success("✅ GRID NORMAL")

    # ----------- TABLE -----------
    st.subheader("📊 Areas")
    df = pd.DataFrame(areas)
    st.dataframe(df[["name","priority","current","predicted","allocated","status"]])

    # ----------- GRAPH -----------        
    st.subheader("📈 Demand Prediction")
    fig, ax = plt.subplots()
    ax.plot(df["current"], label="Current")
    ax.plot(df["predicted"], label="Predicted")
    ax.legend()
    ax.set_facecolor("#121212")
    fig.patch.set_facecolor("#121212")
    st.pyplot(fig)

    # ----------- ALERTS -----------
    st.subheader("🚨 Alerts")
    for area in areas:
        if area["status"] == "Cut":
            st.error(f"{area['name']} supply cut!")
        elif area["status"] == "Increase":
            st.warning(f"{area['name']} demand increased!")                                                                        
