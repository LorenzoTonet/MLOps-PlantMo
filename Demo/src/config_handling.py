import json
from pathlib import Path
import streamlit as st

# -----------------------------
# CONFIG HANDLING
# -----------------------------

def load_config(CONFIG_FILE):
    """
    Load configuration from a JSON file.
    Args:
        CONFIG_FILE (Path): Path to the configuration file.
    Returns:
        dict: Configuration data if file exists, else None.
    """
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
        
def save_config(CONFIG_FILE):
    """
    Save configuration to a JSON file.
    Args:
        CONFIG_FILE (Path): Path to the configuration file.
    """
    config = {
        "sensors": st.session_state.sensors,
        "plants": st.session_state.plants,
        "stdev_sensors": st.session_state.stdev_sensors,
        "thresholds": st.session_state.get("thresholds", {})
    }
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)




