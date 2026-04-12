import streamlit as st
import pandas as pd
import random
import requests

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="GridMind AI | Meta Hackathon",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. ADVANCED UI STYLING (The "Glow" Theme) ---
st.markdown("""
    <style>
    /* Global Background */
    .stApp { background-color: #0B0E14; color: #E0E0E0; }
    
    /* Custom Metric Cards */
    div[data-testid="stMetric"] {
        background-color: #161B22;
        border: 1px solid #30363D;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }
    
    /* Managed Area Cards */
    .area-card {
        background: linear-gradient(145deg, #1c2128, #161b22);
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 15px;
        transition: transform 0.2s, border-color 0.2s;
    }
    .area-card:hover { 
        border-color: #00BFFF; 
        transform: translateY(-3px);
        box-shadow: 0 0 15px rgba(0, 191, 255, 0.1); 
    }
    
    /* Priority Badges */
    .badge {
        padding: 3px 10px;
        border-radius: 6px;
        font-size: 0.65rem;
        font-weight: 800;
        text-transform: uppercase;
        float: right;
        letter-spacing: 0.5px;
    }
    .b-Critical { background: rgba(255, 75, 75, 0.15); color: #FF4B4B; border: 1px solid #FF4B4B; }
    .b-High { background: rgba(255, 165, 0, 0.15); color: #FFA500; border: 1px solid #FFA500; }
    .b-Medium { background: rgba(255, 215, 0, 0.15); color: #FFD700; border: 1px solid #FFD700; }
    .b-Low { background: rgba(76, 175, 80, 0.15); color: #4CAF50; border: 1px solid #4CAF50; }
    /* Custom Buttons */
    .stButton>button {
        width: 100%;
        border-radius: 10px !important;
        background: #00BFFF !important;
        color: #000 !important;
        font-weight: bold !important;
        text-transform: uppercase;
        border: none !important;
        padding: 10px !important;
    }
    .stButton>button:hover {
        background: #009ACD !important;
        box-shadow: 0 0 10px rgba(0, 191, 255, 0.4);
    }
    /* Sidebar Styling */
    section[data-testid="stSidebar"] { background-color: #0D1117; border-right: 1px solid #30363d; }
    </style>
""", unsafe_allow_html=True)

# --- 3. LOGIC & API INTEGRATION ---
def fetch_live_grid_data():
    """Simulates real capacity based on weather data (Open-Meteo)"""
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=12.97&longitude=77.59&current_weather=true" # Bangalore Coordinates
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            temp = response.json()['current_weather']['temperature']
            # Higher temp simulates higher solar yield or peak cooling demand
            return 1000 + (int(temp) * 12)
        return 1100
    except:
        return 1200

# Constants
WEIGHTS = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1}

# Session State Init
if "areas" not in st.session_state: st.session_state.areas = []
if "res" not in st.session_state: st.session_state.res = None

def load_scenario(lvl):
    base_data = [
        ("City Hospital", "Critical", 120), ("Nuclear Plant", "Critical", 90), 
        ("Data Center Hub", "High", 230), ("Gov Complex", "High", 150), 
        ("Metro Mall", "Medium", 180), ("Industrial Park", "Medium", 280),
        ("Res. North", "Low", 140), ("Res. South", "Low", 130)
    ]
    mult = {"Easy": 0.8, "Medium": 1.0, "Hard": 1.4}[lvl]
    st.session_state.areas = [{"name": n, "prio": p, "usage": int(u * mult)} for n, p, u in base_data]

def ai_balance(cap):
    if not st.session_state.areas: return
    results = []
    rem_cap = cap
    # Sort by priority
    sorted_data = sorted(st.session_state.areas, key=lambda x: WEIGHTS[x['prio']], reverse=True)
    for a in sorted_data:
        pred = a['usage'] * random.uniform(0.98, 1.15)
        alloc = min(pred, rem_cap)
        rem_cap -= alloc
        status = "Normal" if alloc >= pred * 0.98 else ("Restricted" if alloc > 0 else "Disconnected")
        results.append({**a, "pred": pred, "alloc": alloc, "status": status})
    st.session_state.res = results

# --- 4. SIDEBAR PANEL ---
with st.sidebar:
    st.markdown("<h2 style='color:#00BFFF;'>🛠️ CONTROL PANEL</h2>", unsafe_allow_html=True)
    
    use_api = st.toggle("🌐 Sync with Real-Time API", value=True)
    cap_val = fetch_live_grid_data() if use_api else 1200
    
    st.divider()
    
    scenario = st.selectbox("Select Scenario", ["Easy", "Medium", "Hard"], index=1)
    if st.button("📥 Load Scenario Data"):
        load_scenario(scenario)
        st.session_state.res = None
        st.rerun()
        
    if st.button("🤖 Run AI Balancing"):
        ai_balance(cap_val)
        
    st.divider()
    with st.expander("➕ Manual Area Entry"):
        name = st.text_input("Area Name")
        prio = st.selectbox("Prio", ["Critical", "High", "Medium", "Low"])
        usage = st.number_input("Demand (MW)", 10, 1000, 100)
        if st.button("Add to Grid"):
            st.session_state.areas.append({"name": name, "prio": prio, "usage": usage})
            st.rerun()

# --- 5. MAIN DASHBOARD ---
st.markdown("<h1 style='color:#00BFFF; margin-bottom:0;'>⚡ GRIDMIND AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#888; margin-top:0;'>INTELLIGENT ENERGY OPTIMIZATION ENGINE</p>", unsafe_allow_html=True)

# Metric Row
total_demand = sum(a['usage'] for a in st.session_state.areas)
util_rate = (total_demand / cap_val) * 100 if cap_val > 0 else 0

m1, m2, m3, m4 = st.columns(4)
m1.metric("MAX CAPACITY", f"{cap_val} MW", delta="API Live" if use_api else None)
m2.metric("CURRENT LOAD", f"{total_demand:.1f} MW")
m3.metric("UTILIZATION", f"{util_rate:.1f}%")
m4.metric("SYSTEM HEALTH", "STABLE" if util_rate < 90 else "WARNING", 
          delta=None if util_rate < 90 else "- Peak Load")

st.divider()

# Managed Areas Grid
st.subheader("🏢 MANAGED GRID SECTORS")
if not st.session_state.areas:
    st.info("No active grid sectors. Load a scenario from the sidebar.")
else:
    area_cols = st.columns(4)
    for idx, area in enumerate(st.session_state.areas):
        with area_cols[idx % 4]:
            st.markdown(f"""
                <div class="area-card">
                    <span class="badge b-{area['prio']}">{area['prio']}</span>
                    <div style="font-size: 1rem; font-weight: bold; color:#FFF;">{area['name']}</div>
                    <div style="margin-top:10px;">
                        <span style="color:#888; font-size:0.8rem;">Demand:</span><br>
                        <span style="color:#00BFFF; font-size:1.5rem; font-weight:bold;">{area['usage']}</span>
                        <span style="color:#00BFFF; font-size:0.8rem;">MW</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

# Results Visualization
if st.session_state.res:
    st.divider()
    res_df = pd.DataFrame(st.session_state.res)
    
    col_graph, col_stats = st.columns([2, 1])
    
    with col_graph:
        st.subheader("📊 Balancing Results")
        st.bar_chart(res_df.set_index('name')[['pred', 'alloc']], color=["#444", "#00BFFF"])
        
    with col_stats:
        st.subheader("📋 Action Report")
        for _, row in res_df.iterrows():
            color = "#4CAF50" if row['status'] == "Normal" else "#FF4B4B"
            st.markdown(f"**{row['name']}**: <span style='color:{color}'>{row['status']}</span> ({row['alloc']:.0f} MW)", unsafe_allow_html=True)
