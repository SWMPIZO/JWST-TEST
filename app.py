import streamlit as st
import numpy as np
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
import time

# --- 1. CONFIGURATION & GMT+7 THEME ---
st.set_page_config(page_title="JWST Deep Space Laboratory", page_icon="🛰️", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0c0f12; }
    h1, h2, h3 { color: #f0f4f8; font-family: 'Segoe UI', sans-serif; }
    div[data-testid="stMetricValue"] { color: #00e5ff; font-weight: bold; }
    .stDateInput div { background-color: #1a233a !important; }
    </style>
""", unsafe_allow_html=True)

st.title("🛰️ JWST Advanced Trajectory & Orbit Analytics Lab")
st.markdown("Configure custom temporal boundaries in **GMT+7 (WIB)** to track real-time telemetry metrics, solar orbits, and precise proximity passes.")

# --- 2. SIDEBAR PARAMETERS (THE CONTROLS) ---
st.sidebar.header("🗓️ Time & Mission Windows (GMT+7)")

# Custom Date Pickers
start_date = st.sidebar.date_input("Mission Start Date", datetime(2026, 1, 1).date())
end_date = st.sidebar.date_input("Mission End Date", datetime(2027, 1, 1).date())

if start_date >= end_date:
    st.error("Error: End Date must be after the Start Date.")
    st.stop()

st.sidebar.markdown("---")
st.sidebar.header("🎬 Timelapse Controls")
play_speed = st.sidebar.slider("🏃 Frame Propagation Speed", min_value=1, max_value=15, value=4)
speed_mult = st.sidebar.slider("🔄 Halo Orbit Frequency Multiplier", min_value=1.0, max_value=5.0, value=2.5, step=0.5)
play_state = st.sidebar.radio("🎮 Player Status", ["Play Timeline", "Pause/Freeze"], horizontal=True)

# --- 3. MATHEMATICAL TRAJECTORY ENGINE ---
# Calculate total delta hours
dt_start = datetime.combine(start_date, datetime.min.time())
dt_end = datetime.combine(end_date, datetime.min.time())
total_hours = int((dt_end - dt_start).total_seconds() / 3600)
total_days = (dt_end - dt_start).days

# Define steps based on timeframe length
steps = max(100, min(total_days * 2, 600))
t_space = np.linspace(0, (total_days / 365.25) * 2 * np.pi, steps)

# Scaled astronomical baselines
EARTH_RADIUS = 50
L2_OFFSET = 11

# Calculate sequential positional vectors
e_x = EARTH_RADIUS * np.cos(t_space)
e_y = EARTH_RADIUS * np.sin(t_space)
e_z = np.zeros(steps)

l2_x = (EARTH_RADIUS + L2_OFFSET) * np.cos(t_space)
l2_y = (EARTH_RADIUS + L2_OFFSET) * np.sin(t_space)

halo_angle = t_space * speed_mult
j_x = l2_x + 3.8 * np.cos(halo_angle)
j_y = l2_y + 3.8 * np.sin(halo_angle)
j_z = 2.8 * np.sin(halo_angle)

# --- 4. TIMELAPSE INDEX MANAGER ---
if "time_idx" not in st.session_state:
    st.session_state.time_idx = 0

if play_state == "Play Timeline":
    st.session_state.time_idx = (st.session_state.time_idx + play_speed) % steps

current_idx = max(1, st.session_state.time_idx)

# Active sliced trajectories up to the current frame index
active_ex, active_ey, active_ez = e_x[:current_idx], e_y[:current_idx], e_z[:current_idx]
active_jx, active_jy, active_jz = j_x[:current_idx], j_y[:current_idx], j_z[:current_idx]

# --- 5. TELEMETRY ANALYTICS GENERATOR ---
current_fraction = current_idx / steps
current_hours_passed = int(total_hours * current_fraction)
current_sim_date = dt_start + timedelta(hours=current_hours_passed)

# Telemetry Counter Algorithms
earth_orbits_completed = (t_space[current_idx-1]) / (2 * np.pi)
sun_orbits_completed = earth_orbits_completed # Since L2 loops the sun locked with Earth

# Earth Pro