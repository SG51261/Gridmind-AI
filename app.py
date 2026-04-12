import streamlit as st
import pandas as pd
import numpy as np
import time
import random
from dataclasses import dataclass, field
from typing import List, Dict

# --- 1. OPENENV DEFINITION (Meta Framework) ---
# We define the Environment using OpenEnv's standard Schema
try:
    from openenv.core.env_server import Environment, Action, Observation, State
except ImportError:
    # Fallback Mock if library isn't installed yet (for UI demo stability)
    class Action: pass
    class Observation: pass
    class State: pass
    class Environment: 
        def reset(self): pass
        def step(self, action): pass

# > DATA MODELS
@dataclass
class GridAction(Action):
    allocations: Dict[str, float]  # Allocating MW to each sector

@dataclass
class GridObservation(Observation):
    sectors: List[Dict]           # Current status of all sectors
    total_load: float
    grid_health: float

@dataclass
class GridState(State):
    capacity: float
    step_count: int = 0

# > ENVIRONMENT LOGIC
class GridControlEnv(Environment):
    def __init__(self, capacity):
        self.capacity = capacity
        self.areas = [
            {"name": "City Hospital", "prio": "Critical", "base": 120},
            {"name": "Nuclear Control", "prio": "Critical", "base": 95},
            {"name": "Data Center Hub", "prio": "High", "base": 240},
            {"name": "Metro Center", "prio": "Medium", "base": 180},
            {"name": "Res. North", "prio": "Low", "base": 130}
        ]
        self.current_step = 0

    def reset(self) -> GridObservation:
        self.current_step = 0
        # Generate initial demand with noise
        current_status = []
        total_load = 0
        for area in self.areas:
            usage = int(area['base'] * random.uniform(0.9, 1.1))
            current_status.append({
                **area, 
                "usage": usage, 
                "alloc": 0, 
                "status": "Waiting"
            })
            total_load += usage
        
        return GridObservation(
            sectors=current_status,
            total_load=total_load,
            grid_health=100.0
        )

    def step(self, action: GridAction) -> GridObservation:
        self.current_step += 1
        updated_sectors = []
        total_load = 0
        
        # Apply Allocations & Calculate Physics
        for i, sector in enumerate(self.areas):
            # Re-simulate demand fluctuation for the next step
            usage = int(sector['base'] * random.uniform(0.95, 1.15))
            allocated = action.allocations.get(sector['name'], 0)
            
            # Determine Status
            if allocated >= usage * 0.98:
                status = "Normal"
            elif allocated > 0:
                status = "Restricted"
            else:
                status = "Offline"
            
            updated_sectors.append({
                "name": sector['name'],
                "prio": sector['prio'],
                "usage": usage,
                "alloc": allocated,
                "status": status
            })
            total_load += usage

        # Calculate Grid Health (Simple heuristic)
        health = 100 - (max(0, total_load - self.capacity) / 10)

        return GridObservation(
            sectors=updated_sectors,
            total_load=total_load,
            grid_health=health
        )

# --- 2. PAGE CONFIG & CSS ---
st.set_page_config(page_title="GridMind AI | OpenEnv Core", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0B0E14; color: #E0E0E0; }
    div[data-testid="stMetric"] { background-color: #161B22; border: 1px solid #30363D; border-radius: 12px; padding: 20px; }
    .area-card {
        background: linear-gradient(145deg, #1c2128, #161b22);
        border: 1px solid #30363d; border-radius: 12px; padding: 18px; margin-bottom: 15px;
    }
    .area-card:hover { border-color: #00BFFF; box-shadow: 0 0 10px rgba(0, 191, 255, 0.1); }
    .badge { padding: 3px 8px; border-radius: 5px; font-size: 0.65rem; font-weight: bold; float: right; text-transform: uppercase; }
    .b-Critical { border: 1px solid #FF4B4B; color: #FF4B4B; background: rgba(255, 75, 75, 0.1); }
    .b-High { border: 1px solid #FFA500; color: #FFA500; background: rgba(255, 165, 0, 0.1); }
    .b-Medium { border: 1px solid #FFD700; color: #FFD700; background: rgba(255, 215, 0, 0.1); }
    .b-Low { border: 1px solid #4CAF50; color: #4CAF50; background: rgba(76, 175, 80, 0.1); }
    .stButton>button { background: #00BFFF !important; color: black !important; border-radius: 8px; border: none; font-weight: bold;}
    </style>
""", unsafe_allow_html=True)

# --- 3. SECURITY & API CONFIGURATION ---
# SECURE PATTERN: Check st.secrets first, fallback to variable for testing
API_KEY = st.secrets.get("GRIDMIND_API_KEY", "sk-emergent-77b119a204cBbB18eA")

def get_capacity():
    # Simulate API fetch
    t = time.time()
    return int(1100 + np.sin(t/10) * 50 + random.randint(-5, 5))

# --- 4. SESSION STATE INITIALIZATION ---
if "env" not in st.session_state:
    # Initialize OpenEnv Environment
    st.session_state.env = GridControlEnv(capacity=1200)
    # Get initial observation
    st.session_state.obs = st.session_state.env.reset()

# --- 5. SIDEBAR CONTROLS ---
with st.sidebar:
    st.title("🛠️ Control Panel")
    st.caption(f"🔑 API Key Loaded: ...{API_KEY[-4:]}")
    
    capacity = get_capacity()
    st.metric("Grid Capacity", f"{capacity} MW")
    
    st.divider()
    
    # AI AGENT LOGIC (The "Brain")
    if st.button("🤖 EXECUTE AI BALANCE"):
        # 1. Read Observation
        current_obs = st.session_state.obs
        rem_cap = capacity
        allocations = {}
        
        # 2. Determine Policy (Sort by Priority)
        # Mapping Prio Strings to Weights
        weights = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1}
        sorted_sectors = sorted(
            current_obs.sectors, 
            key=lambda x: weights.get(x['prio'], 1), 
            reverse=True
        )
        
        # 3. Calculate Action
        for sector in sorted_sectors:
            demand = sector['usage']
            alloc = min(demand, rem_cap)
            allocations[sector['name']] = alloc
            rem_cap -= alloc
            
        # 4. Step the Environment (OpenEnv Standard)
        action = GridAction(allocations=allocations)
        new_obs = st.session_state.env.step(action)
        st.session_state.obs = new_obs
        st.rerun()

    if st.button("🔄 Reset Environment"):
        st.session_state.obs = st.session_state.env.reset()
        st.rerun()

# --- 6. MAIN UI ---
st.markdown("<h1 style='color:#00BFFF;'>⚡ GRIDMIND AI <span style='font-size:0.5em; color:#666;'>| OpenEnv Integrated</span></h1>", unsafe_allow_html=True)

obs = st.session_state.obs

# Metrics
m1, m2, m3, m4 = st.columns(4)
m1.metric("CAPACITY", f"{capacity} MW")
m2.metric("TOTAL LOAD", f"{obs.total_load} MW")
util = (obs.total_load / capacity) * 100
m3.metric("UTILIZATION", f"{util:.1f}%")
m4.metric("GRID HEALTH", f"{obs.grid_health:.1f}%")

st.divider()

# Grid Visualization
st.subheader("🏢 Sector Status (Live Observation)")
cols = st.columns(4)
for idx, sector in enumerate(obs.sectors):
    with cols[idx % 4]:
        # Determine color based on status
        val_color = "#00BFFF"
        if sector['status'] == "Restricted": val_color = "#FFA500"
        if sector['status'] == "Offline": val_color = "#FF4B4B"
        
        st.markdown(f"""
            <div class="area-card">
                <span class="badge b-{sector['prio']}">{sector['prio']}</span>
                <div style="font-weight: bold; color: white;">{sector['name']}</div>
                <div style="margin-top:10px;">
                    <span style="color:#888; font-size:0.8rem;">Demand: {sector['usage']} MW</span><br>
                    <span style="color:{val_color}; font-size:1.3rem; font-weight:bold;">
                        {sector['alloc']} MW
                    </span>
                </div>
                <div style="margin-top:5px; font-size:0.8rem; color:{val_color};">
                    ● {sector['status']}
                </div>
            </div>
        """, unsafe_allow_html=True)

# Charting
if obs.total_load > 0:
    st.divider()
    st.subheader("📊 Allocation Telemetry")
    df = pd.DataFrame(obs.sectors)
    st.bar_chart(df.set_index("name")[["usage", "alloc"]], color=["#333333", "#00BFFF"])
