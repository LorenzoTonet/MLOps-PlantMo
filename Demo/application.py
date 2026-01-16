#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Streamlit dashboard for greenhouse monitoring
Reads from a Flask API /stream endpoint and plots sensor data.
"""

import streamlit as st
import pandas as pd
import requests
import json
import time
import matplotlib.pyplot as plt
import random
from datetime import datetime

from src.config_handling import *
from src.plotting_functions import *
from src.data_generators import *
from src.plant_data_management import *

# -----------------------------
# STREAMLIT CONFIG
# -----------------------------

CONFIG_FILE = Path("greenhouse_info.json")


st.set_page_config(page_title="Greenhouse Monitor", layout="wide")
st.title("🌱 Greenhouse Monitoring Dashboard")

config = load_config(CONFIG_FILE)

if "sensors" not in st.session_state:
    st.session_state.sensors = config["sensors"]

if "plants" not in st.session_state:
    st.session_state.plants = config["plants"]

# -----------------------------
# SIDEBAR - CONNECTION SETTINGS
# -----------------------------
st.sidebar.header("🔌 Connection Settings")

connection_mode = st.sidebar.radio(
    "Data Source",
    ["Flask Server", "Random Data"],
    index=1  # Default to Random for testing
)

if connection_mode == "Flask Server":
    default_ip = st.session_state.get("ip", "127.0.0.1")
    default_port = st.session_state.get("port", "8000")
    
    ip = st.sidebar.text_input("Server IP", default_ip)
    port = st.sidebar.text_input("Server Port", default_port)
    
    st.session_state.ip = ip
    st.session_state.port = port
    
    STREAM_URL = f"http://{ip}:{port}/stream"
    st.sidebar.markdown(f"**Connected to:** `{STREAM_URL}`")
else:
    st.sidebar.markdown("**Mode:** 🎲 Random Data Generation")

st.sidebar.markdown("---")

# -----------------------------
# SIDEBAR - PLANT SELECTION
# -----------------------------
st.sidebar.header("🪴 Plant Selection")

selected_plant = st.sidebar.selectbox(
    "Select Plant to Monitor",
    st.session_state.plants,
    key="selected_plant",
    index=0
)


st.sidebar.markdown("---")

with st.sidebar.expander("➕ Add New Plant"):
    with st.form("add_plant_form", clear_on_submit=True):
        new_plant_name = st.text_input("Plant name")
        submitted = st.form_submit_button("Add")

        if submitted and new_plant_name.strip():
            add_plant(new_plant_name, CONFIG_FILE)
            st.success(f"🌱 Plant '{new_plant_name}' added")
            st.rerun()

with st.sidebar.expander("🗑️ Remove Plant"):
    if st.session_state.plants:
        plant_to_remove = st.selectbox(
            "Select plant to remove",
            st.session_state.plants,
            key="plant_to_remove",
        )

        confirm = st.button("Remove", type="primary")

        if confirm:
            remove_plant(plant_to_remove, CONFIG_FILE)
            st.success(f"🗑️ Plant '{plant_to_remove}' removed")
            st.rerun()
    else:
        st.info("No plants to remove.")

st.sidebar.markdown("---")
# -----------------------------
# PARAMETERS
# -----------------------------
st.sidebar.header("⚙️ Settings")
REFRESH_INTERVAL = st.sidebar.slider("Refresh interval (seconds)", 0.1, 5.0, 1.0)
MAX_POINTS = st.sidebar.slider("Number of samples to show", 50, 500, 150)

# Sensori per ogni pianta
SENSORS = st.session_state.sensors

# Fixed y-axis ranges for each sensor
Y_RANGES = {
    "soil_humidity": (0, 100),      # %
    "air_humidity": (0, 100),       # %
    "light": (0, 1000),             # lux
    "temperature": (10, 40),        # °C
}

SENSOR_LABELS = {
    "soil_humidity": "Soil Humidity (%)",
    "air_humidity": "Air Humidity (%)",
    "light": "Light (lux)",
    "temperature": "Temperature (°C)"
}

SENSOR_COLORS = {
    "soil_humidity": "#8B4513",
    "air_humidity": "#4A90E2",
    "light": "#F5A623",
    "temperature": "#E74C3C"
}

# -----------------------------
# FUNCTIONS
# -----------------------------

def stream_data(url):
    """Generator to read data lines from Flask SSE endpoint."""
    try:
        with requests.get(url, stream=True, timeout=10) as r:
            for line in r.iter_lines():
                if line and line.startswith(b"data:"):
                    payload = line.replace(b"data: ", b"").decode("utf-8")
                    try:
                        yield json.loads(payload)
                    except json.JSONDecodeError:
                        continue
    except Exception as e:
        st.error(f"Stream error: {e}")
        return



# -----------------------------
# INITIALIZE SESSION STATE
# -----------------------------

# Initialize all plants
for plant in st.session_state.plants:
    init_plant_data(plant)

# -----------------------------
# DISPLAY CURRENT PLANT STATUS
# -----------------------------
st.subheader(f"📊 Monitoring: {selected_plant}")

# Placeholder for charts
placeholder = st.empty()

# Info message
if len(st.session_state[f"data_{selected_plant}"]) == 0:
    st.info("🟢 Waiting for live data...")

# -----------------------------
# LIVE PLOTTING LOOP
# -----------------------------
if connection_mode == "Random Data":
    snapshot = generate_snapshot()
else:
    data_gen = stream_data(STREAM_URL)

for sample in snapshot:
    # Il sample deve contenere: {"plant": "Tomato_1", "timestamp": ..., "soil_humidity": ..., etc.}
    
    if "plant" not in sample:
        continue
    
    plant_name = sample["plant"]
    
    # Verifica che la pianta esista
    if plant_name not in st.session_state.plants:
        continue
    
    plant = sample["plant"]
    df = st.session_state[f"data_{plant}"]

    df.loc[len(df)] = sample

    if len(df) > MAX_POINTS:
        df = df.iloc[-MAX_POINTS:]

    st.session_state[f"data_{plant}"] = df
    
    # Plot only if this is the selected plant
    if plant_name == selected_plant and len(df) > 0:
        fig, axes = plt.subplots(2, 2, figsize=(14, 8))
        axes = axes.flatten()
        
        for i, sensor in enumerate(SENSORS):
            ax = axes[i]
            ax.plot(df["timestamp"], df[sensor], 
                   linewidth=2, 
                   color=SENSOR_COLORS[sensor],
                   marker='o',
                   markersize=3)
            
            # Current value
            current_value = df[sensor].iloc[-1]
            ax.set_title(f"{SENSOR_LABELS[sensor]} - Current: {current_value:.1f}", 
                        fontsize=12, 
                        fontweight="bold")
            ax.set_ylim(Y_RANGES[sensor])
            ax.set_xlabel("Timestamp")
            ax.set_ylabel(SENSOR_LABELS[sensor])
            ax.grid(True, linestyle="--", alpha=0.4)
        
        plt.tight_layout()
        placeholder.pyplot(fig)
        plt.close(fig)
    
    time.sleep(REFRESH_INTERVAL)