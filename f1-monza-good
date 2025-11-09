import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import random

st.set_page_config(layout="wide")
st.title("F1 Simulator - Monza 2025")
st.write("Du kör McLaren! 🚗💨")

# ----------------------
# Inställningar
# ----------------------
laps_total = st.sidebar.number_input("Totala varv", min_value=1, value=10)
track_length = st.sidebar.number_input("Varvlängd (km)", min_value=1, value=5)

# ----------------------
# Förare 2025
# ----------------------
drivers = [
    {"name": "VER", "team": "Red Bull", "color":"#1E41FF"},
    {"name": "TSU", "team": "Red Bull", "color":"#1E41FF"},
    {"name": "LEC", "team": "Ferrari", "color":"#FF2800"},
    {"name": "HAM", "team": "Ferrari", "color":"#FF2800"},
    {"name": "RUS", "team": "Mercedes", "color":"#00D2BE"},
    {"name": "ANT", "team": "Mercedes", "color":"#00D2BE"},
    {"name": "NOR", "team": "McLaren", "color":"#FF8700"},
    {"name": "PIA", "team": "McLaren", "color":"#FF8700"},
    {"name": "ALO", "team": "Aston Martin", "color":"#006F62"},
    {"name": "STR", "team": "Aston Martin", "color":"#006F62"},
    {"name": "GAS", "team": "Alpine", "color":"#0090FF"},
    {"name": "DOO", "team": "Alpine", "color":"#0090FF"},
    {"name": "ALB", "team": "Williams", "color":"#005AFF"},
    {"name": "COL", "team": "Williams", "color":"#005AFF"},
    {"name": "HAD", "team": "Racing Bulls", "color":"#FF0000"},
    {"name": "LAW", "team": "Racing Bulls", "color":"#FF0000"},
    {"name": "HUL", "team": "Sauber", "color":"#E5E5E5"},
    {"name": "ZHO", "team": "Sauber", "color":"#E5E5E5"},
    {"name": "BEA", "team": "Haas", "color":"#FFFFFF"},
    {"name": "OCO", "team": "Haas", "color":"#FFFFFF"},
]

# Initiera session state för varje förare
for d in drivers:
    if "battery" not in d:
        d["battery"] = 100
    if "damage" not in d:
        d["damage"] = 0
    if "dnf" not in d:
        d["dnf"] = False
    if "dsq" not in d:
        d["dsq"] = False

if "lap" not in st.session_state:
    st.session_state.lap = 1
if "tyre_wear" not in st.session_state:
    st.session_state.tyre_wear = 0
if "pit_done" not in st.session_state:
    st.session_state.pit_done = False
if "fastest_lap" not in st.session_state:
    st.session_state.fastest_lap = 999
if "race_paused" not in st.session_state:
    st.session_state.race_paused = False
if "sc_active" not in st.session_state:
    st.session_state.sc_active = False

# ----------------------
# Slumpade incidenter / regelbrott
# ----------------------
def random_incident_or_penalty(driver):
    if driver["dnf"] or driver["dsq"]:
        return "", ""
    r = random.random()
    if r < 0.04:
        driver["damage"] += random.uniform(2,4)
        return f"Kollision! {driver['name']} skadas, tidsstraff +5s", "collision"
    elif r < 0.12:
        return f"Varning: {driver['name']} bryter mot reglerna! +3s", "warning"
    elif r < 0.14:
        driver["dsq"] = True
        return f"{driver['name']} är diskad! DSQ", "dsq"
    elif r < 0.16:
        driver["dnf"] = True
        return f"{driver['name']} bryter loppet (DNF)", "dnf"
    else:
        return "", ""

# ----------------------
# Safety Car / Röd flagg
# ----------------------
def check_safety_or_red_flag():
    sc_msg = ""
    rf_msg = ""
    if random.random() < 0.03:
        st.session_state.sc_active = True
        sc_msg = "Safety Car ute på banan! Alla varvtider ökar."
    else:
        st.session_state.sc_active = False
    if random.random() < 0.01:
        st.session_state.race_paused = True
        rf_msg = "Röd flagg! Loppet pausas."
    else:
        st.session_state.race_paused = False
    return sc_msg, rf_msg

# ----------------------
# Kör nästa varv
# ----------------------
if st.button("Nästa varv") and not st.session_state.race_paused:
    st.session_state.lap += 1
    st.session_state.tyre_wear = min(100, st.session_state.tyre_wear + random.uniform(5,15))

    lap_times = []
    for d in drivers:
        if d["dnf"] or d["dsq"]:
            lap_times.append(np.nan)
            continue

        # Batteri påverkar prestanda
        battery_factor = 1 - ((100-d["battery"])/200)  # högre batteri = snabbare
        lap_time = random.uniform(75,85) * battery_factor

        # DRS slumpmässigt
        if random.random() < 0.3:
            lap_time -= random.uniform(0.2,0.5)

        # Safety Car påverkan
        if st.session_state.sc_active:
            lap_time += random.uniform(5,10)

        d["battery"] = max(0, d["battery"] - random.uniform(5,15))

        # Incidenter och regelbrott
        msg, incident_type = random_incident_or_penalty(d)
        if msg != "":
            st.warning(msg)
            if incident_type == "collision":
                lap_time += 5
            elif incident_type == "warning":
                lap_time += 3

        lap_times.append(round(lap_time,2))

        # Uppdatera snabbaste varv
        if lap_time < st.session_state.fastest_lap:
            st.session_state.fastest_lap = lap_time

    sc_msg, rf_msg = check_safety_or_red_flag()
    if sc_msg:
        st.info(sc_msg)
    if rf_msg:
        st.error(rf_msg)

# ----------------------
# BOX-knapp
# ----------------------
if st.button("BOX!"):
    st.session_state.tyre_wear = 0
    for d in drivers:
        if not d["dnf"] and not d["dsq"]:
            d["damage"] = max(0, d["damage"] - random.uniform(0.5,2))
    st.session_state.pit_done = True
    st.success("Pitstop utförd! Däck bytta ✅")

# ----------------------
# Leaderboard
# ----------------------
positions = np.argsort([t if t==t else 999 for t in [random.uniform(75,85) for _ in drivers]]) + 1
df = pd.DataFrame({
    "Driver": [d["name"] for d in drivers],
    "Team": [d["team"] for d in drivers],
    "Lap Time": [np.nan if d["dnf"] or d["dsq"] else random.uniform(75,85) for d in drivers],
    "Tyre Wear": [round(st.session_state.tyre_wear,1) for _ in drivers],
    "Damage": [round(d["damage"],1) for d in drivers],
    "Battery": [round(d["battery"],1) for d in drivers],
    "Status": ["DNF" if d["dnf"] else "DSQ" if d["dsq"] else "OK" for d in drivers]
})

st.subheader("Leaderboard")
st.table(df)

# ----------------------
# Bilstatus McLaren
# ----------------------
st.subheader("Bilstatus - McLaren")
for d in drivers:
    if d["team"]=="McLaren" and not d["dnf"] and not d["dsq"]:
        st.write(f"Förare: {d['name']}")
        st.write(f"Varv: {st.session_state.lap}/{laps_total}")
        st.write(f"Däckslitage: {st.session_state.tyre_wear:.1f}%")
        st.write(f"Skador: {d['damage']:.1f}/10")
        st.write(f"Batteristatus: {d['battery']:.1f}%")
        st.write(f"Snabbaste varv: {st.session_state.fastest_lap:.2f}s")

# ----------------------
# Trackmap
# ----------------------
st.subheader("Trackmap")
trackmap = go.Figure()
for d in drivers:
    if d["dnf"] or d["dsq"]:
        continue
    trackmap.add_trace(go.Scatter(
        x=[random.randint(0,100)],
        y=[random.randint(0,100)],
        mode="markers+text",
        marker=dict(size=12, color=d["color"]),
        text=[d["name"]],
        textposition="top center"
    ))
trackmap.update_layout(title="Trackmap Monza 2025", xaxis_title="X", yaxis_title="Y", showlegend=False)
st.plotly_chart(trackmap, use_container_width=True)
