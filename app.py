import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="GridMind AI", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; }
    div[data-testid="stMetricValue"] { color: white !important; }
    .stButton>button { 
        width: 100%; background-color: #00BFFF !important; color: black !important; 
        font-weight: bold !important; border-radius: 8px !important; text-transform: uppercase;
    }
    .card { 
        background-color: #1C1F26; border: 1px solid #2D323B; border-radius: 12px; 
        padding: 10px; margin-bottom: 10px; color: white; 
    }
    .badge { padding: 2px 6px; border-radius: 4px; font-size: 0.6rem; font-weight: bold; float: right; }
    .b-Critical { background: #FF4B4B; } .b-High { background: #FFA500; }
    .b-Medium { background: #FFD700; color: black; } .b-Low { background: #4CAF50; }
    </style>
""", unsafe_allow_html=True)

CAPACITY = 1200
WEIGHTS = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1}

if "areas" not in st.session_state: st.session_state.areas = []
if "res" not in st.session_state: st.session_state.res = None

def load_data(lvl):
    base = [("Hospital", "Critical", 100), ("Nuclear", "Critical", 80), ("DataCenter", "Critical", 200),
            ("GovOffice", "High", 150), ("Industry", "High", 250), ("CityCenter", "Medium", 200),
            ("ResNorth", "Low", 150), ("ResSouth", "Low", 150)]
    m = {"Easy": 0.7, "Medium": 1.0, "Hard": 1.5}[lvl]
    st.session_state.areas = [{"name": n, "priority": p, "usage": int(u*m)} for n, p, u in base]

def balance():
    for a in st.session_state.areas: a['pred'] = a['usage'] * random.uniform(0.9, 1.3)
    sorted_a = sorted(st.session_state.areas, key=lambda x: WEIGHTS[x['priority']], reverse=True)
    rem, final = CAPACITY, []
    for a in sorted_a:
        alloc = min(a['pred'], rem)
        rem -= alloc
        stat = "Normal" if alloc >= a['pred']*0.98 else ("Reduce" if alloc > 0 else "Cut")
        final.append({**a, "alloc": alloc, "status": stat})
    st.session_state.res = final

st.markdown("<h1 style='text-align:center; color:#00BFFF;'>⚡ GRIDMIND AI</h1>", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
with c1:
    if st.button("➕ Add Area"):
        with st.popover("Details"):
            name = st.text_input("Name")
            pri = st.selectbox("Priority", list(WEIGHTS.keys()))
            use = st.number_input("MW", 10, 1000, 100)
            if st.button("Save"):
                st.session_state.areas.append({"name": name, "priority": pri, "usage": use})
                st.rerun()
with c2:
    lvl = st.selectbox("Level", ["Easy", "Medium", "Hard"])
    if st.button("📥 Load Scenario"):
        load_data(lvl)
        st.rerun()
with c3:
    if st.button("🤖 AI Balance Grid"):
        balance()

load = sum(a['usage'] for a in st.session_state.areas)
util = (load/CAPACITY)*100 if CAPACITY > 0 else 0
m1, m2, m3, m4 = st.columns(4)
m1.metric("Capacity", f"{CAPACITY} MW")
m2.metric("Load", f"{load:.1f} MW")
m3.metric("Util", f"{util:.1f}%")
m4.metric("Status", "NORMAL" if util < 90 else "OVERLOAD")

st.subheader("Managed Areas")
cols = st.columns(4)
for i, a in enumerate(st.session_state.areas):
    with cols[i % 4]:
        st.markdown(f'<div class="card"><span class="badge b-{a["priority"]}">{a["priority"]}</span><b>{a["name"]}</b><br><span style="color:gray">Usage:</span> <span style="color:#00BFFF">{a["usage"]} MW</span></div>', unsafe_allow_html=True)

if st.session_state.res:
    st.divider()
    df = pd.DataFrame(st.session_state.res)
    st.table(df[['name', 'priority', 'pred', 'alloc', 'status']])
    st.subheader("Predicted vs Allocated Load")
    st.bar_chart(df.set_index('name')[['pred', 'alloc']])
