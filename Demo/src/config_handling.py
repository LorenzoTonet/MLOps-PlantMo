import json
from pathlib import Path
import streamlit as st
import random
import time
import pandas as pd

from datetime import datetime


# -----------------------------
# CONFIG HANDLING
# -----------------------------

def load_config(CONFIG_FILE):
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
        
def save_config(CONFIG_FILE):
    config = {
        "sensors": st.session_state.sensors,
        "plants": st.session_state.plants,
    }
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)




