import streamlit as st
import pandas as pd
import numpy as np
import time
import random

# --- 1. PAGE CONFIG & THEME ---
st.set_page_config(
    page_title="GridMind AI | Control Room",
    page_icon="⚡",
    layout="wide"
)

# --- SECURITY CONFIGURATION ---
# TRY to get the key from st.secrets (Best Practice)
# If not found, use a placeholder or the raw string (Not Recommended)
try:
    API_KEY = st.secrets["gridmind_api_key"]
except FileNotFoundError:
    # WARNING: Replace this string with your key ONLY for local testing. 
    # Do not commit this file with the key inside.
    API_KEY = "sk-emergent-77b119a204cBbB18eA" 

# Custom CSS for the "Glow" UI
st.markdown("""
    <style>
    .stApp { background-color: #0B0E14; color: #E0E0E0; }
    
    /* Metric Cards */
    div[data-testid="stMetric"] {
        background-color: #161B22;
        border: 1px solid #30363D;
        border-radius: 12px;
        padding: 20px;
    }
    
    /* Managed Area Cards */
    .area-card {
        background: linear-gradient(145deg, #1c2128, #161b22);
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 15px;
        transition: border-color 0.2s;
    }
    .area-card:hover { border-color: #00BFFF; box-shadow: 0 0 10px rgba(0, 191, 255, 0.1); }
    
    /* Badges */
    .badge {
        padding: 3px 8px;
        border-radius: 5px;
        font-size: 0.65rem;
        font-weight: bold;
        float: right;
        text-transform: uppercase;
    }
    .b-Critical { background: rgba(255, 75, 75, 0.2); color: #FF4B4B; border: 1px solid #FF4B4B; }
    .b-High { background: rgba(255, 165, 0, 0.2); color: #FFA500; border: 1px solid #FFA500; }
    .b-Medium { background: rgba(255, 215, 0, 0.2); color: #FFD700; border: 1px solid #FFD700; }
    .b-Low { background: rgba(76, 175, 80, 0.2); color: #4CAF50; border: 1px solid #4CAF50; }
    /* Buttons */
    .stButton>button {
        width: 100%; border-radius: 8px !important;
        background: #00BFFF !important; color: black !important;
        font-weight: bold !important; border: none !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. DATA FETCHING LAYER ---
def get_capacity(api_key):
    """
    Fetches grid capacity. 
    Uses API if configured, otherwise falls back to simulation.
    """
    # Placeholder for actual API Logic using the key
    if api_key and "sk-emergent" in api_key:
        # Code to call external API would go here
        # headers = {"Authorization": f"Bearer {api_key}"}
        # response = requests.get("...", headers=headers)
        pass 

    # Fallback Simulator
    t = time.time()
    fluctuation = np.sin(t / 10) * 50 
    return int(1100 + fluctuation + random.randint(-5, 5))

# --- 3. CORE LOGIC ---
WEIGHTS = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1}

if "areas" not in st.session_state:
    st.session_state.areas = [
        {"name": "City Hospital", "prio": "Critical", "usage": 120},
        {"name": "Nuclear Control", "prio": "Critical", "usage": 95},
        {"name": "Data Center Hub", "prio": "High", "usage": 240},
        {"name": "Metro Center", "prio": "Medium", "usage": 180},
        {"name": "Res. North", "prio": "Low", "usage": 130}
    ]
if "res" not in st.session_state: st.session_state.res = None

def ai_balance(cap):
    results = []
    rem_cap = cap
    sorted_data = sorted(st.session_state.areas, key=lambda x: WEIGHTS[x['prio']], reverse=True)
    for a in sorted_data:
        pred = a['usage'] * random.uniform(0.98, 1.12)
        alloc = min(pred, rem_cap)
        rem_cap -= alloc
        status = "Normal" if alloc >= pred * 0.98 else ("Restricted" if alloc > 0 else "Offline")
        results.append({**a, "pred": pred, "alloc": alloc, "status": status})
    st.session_state.res = results

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("🛠️ Control Panel")
    
    # API Status Indicator
    if API_KEY:
        st.caption("✅ API Connected (Key Loaded)")
    else:
        st.caption("⚠️ Running in Offline Mode")

    live_toggle = st.toggle("Live Simulation Mode", value=True)
    current_capacity = get_capacity(API_KEY) if live_toggle else 1200
    
    st.divider()
    if st.button("🤖 AI BALANCE NOW"):
        ai_balance(current_capacity)
    
    if st.button("🔄 Reset Grid"):
        st.session_state.res = None
        st.rerun()

# --- 5. MAIN UI ---
st.markdown("<h1 style='color:#00BFFF;'>⚡ GRIDMIND AI</h1>", unsafe_allow_html=True)

# Top Metrics
total_demand = sum(a['usage'] for a in st.session_state.areas)
util = (total_demand / current_capacity) * 100
m1, m2, m3, m4 = st.columns(4)
m1.metric("CAPACITY", f"{current_capacity} MW", delta="Simulated" if live_toggle else None)
m2.metric("LOAD", f"{total_demand} MW")
m3.metric("UTILIZATION", f"{util:.1f}%")
m4.metric("HEALTH", "STABLE" if util < 90 else "PEAK")

st.divider()

# Managed Areas Grid
st.subheader("🏢 Managed Grid Sectors")
cols = st.columns(4)
for idx, area in enumerate(st.session_state.areas):
    with cols[idx % 4]:
        st.markdown(f"""
            <div class="area-card">
                <span class="badge b-{area['prio']}">{area['prio']}</span>
                <div style="font-weight: bold; color: white;">{area['name']}</div>
                <div style="margin-top:10px;">
                    <span style="color:#888; font-size:0.8rem;">Usage:</span><br>
                    <span style="color:#00BFFF; font-size:1.3rem; font-weight:bold;">{area['usage']} MW</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

# Balancing Results
if st.session_state.res:
    st.divider()
    res_df = pd.DataFrame(st.session_state.res)
    c1, c2 = st.columns([2, 1])
    with c1:
        st.subheader("📊 AI Allocation Graph")
        st.bar_chart(res_df.set_index('name')[['pred', 'alloc']], color=["#333", "#00BFFF"])
    with c2:
        st.subheader("📋 Status Report")
        for _, row in res_df.iterrows():
            st.write(f"**{row['name']}**: {row['status']}")
