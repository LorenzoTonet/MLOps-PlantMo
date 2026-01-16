import streamlit as st
import random
import time

from datetime import datetime

# -----------------------------
# RANDOM DATA GENERATION
# -----------------------------

def generate_random_data(plant_name):
    """Generate random sensor data for a plant."""
    return {
        "plant": plant_name,
        "timestamp": datetime.now().strftime("%H:%M"),
        "soil_humidity": random.uniform(40, 80),
        "air_humidity": random.uniform(50, 90),
        "light": random.uniform(200, 800),
        "temperature": random.uniform(18, 32)
    }


def random_data_generator():
    """Generator for random data for all plants."""
    while True:
        # Generate data for a random plant
        plant = random.choice(st.session_state.plants)
        yield generate_random_data(plant)

        time.sleep(0.5)  # Generate data every 0.5 seconds

def generate_snapshot():
    timestamp = datetime.now()
    return [
        {
            "plant": plant,
            "timestamp": timestamp,
            "soil_humidity": random.uniform(40, 80),
            "air_humidity": random.uniform(50, 90),
            "light": random.uniform(200, 800),
            "temperature": random.uniform(18, 32),
        }
        for plant in st.session_state.plants
    ]
