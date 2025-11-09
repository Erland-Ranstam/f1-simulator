import streamlit as st
import numpy as np
import plotly.graph_objects as go
import random
import time

st.set_page_config(layout="wide")
st.title("F1 Simulator - Monza 2025 (Full Real Time)")
st.write("Du kör McLaren! 🚗💨")

# ----------------------
# Tracklayout Monza (exempel)
# ----------------------
track_x = np.array([0,10,20,30,40,50,60,70,80,90,100,90,80,70,60,50,40,30,20,10,0])
track_y = np.array([0,5,10,15,20,25,20,15,10,5,0,-5,-10,-15,-20,-25,-20,-15,-10,-5,0])
track_length = len(track_x)

# ----------------------
# Förare
# ----------------------
drivers = [
    {"name":"NOR","team":"McLaren","color":"#FF8700","pos":0,"lap":1,"distance":0,"speed":1.0,"lap_time":0.0,
     "lap_times":[],"dnf":False,"dsq":False,"damage":0,"battery":100,"tyre_wear":0},
    {"name":"PIA","team":"McLaren","color":"#FF8700","pos":5,"lap":1,"distance":5,"speed":1.0,"lap_time":0.0,
     "lap_times":[],"dnf":False,"dsq":False,"damage":0,"battery":100,"tyre_wear":0},
    {"name":"VER","team":"Red Bull","color":"#1E41FF","pos":10,"lap":1,"distance":10,"speed":1.0,"lap_time":0.0,
     "lap_times":[],"dnf":False,"dsq":False,"damage":0,"battery":100,"tyre_wear":0},
    {"name":"TSU","team":"Red Bull","color":"#1E41FF","pos":15,"lap":1,"distance":15,"speed":1.0,"lap_time":0.0,
     "lap_times":[],"dnf":False,"dsq":False,"damage":0,"battery":100,"tyre_wear":0},
    {"name":"LEC","team":"Ferrari","color":"#FF2800","pos":20,"lap":1,"distance":20,"speed":1.0,"lap_time":0.0,
     "lap_times":[],"dnf":False,"dsq":False,"damage":0,"battery":100,"tyre_wear":0},
    {"name":"HAM","team":"Ferrari","color":"#FF2800","pos":25,"lap":1,"distance":25,"speed":1.0,"lap_time":0.0,
     "lap_times":[],"dnf":False,"dsq":False,"damage":0,"battery":100,"tyre_wear":0},
    {"name":"RUS","team":"Mercedes","color":"#00D2BE","pos":30,"lap":1,"distance":30,"speed":1.0,"lap_time":0.0,
     "lap_times":[],"dnf":False,"dsq":False,"damage":0,"battery":100,"tyre_wear":0},
    {"name":"ANT","team":"Mercedes","color":"#00D2BE","pos":35,"lap":1,"distance":35,"speed":1.0,"lap_time":0.0,
     "lap_times":[],"dnf":False,"dsq":False,"damage":0,"battery":100,"tyre_wear":0},
    {"name":"ALO","team":"Aston Martin","color":"#006F62","pos":40,"lap":1,"distance":40,"speed":1.0,"lap_time":0.0,
     "lap_times":[],"dnf":False,"dsq":False,"damage":0,"battery":100,"tyre_wear":0},
    {"name":"STR","team":"Aston Martin","color":"#006F62","pos":45,"lap":1,"distance":45,"speed":1.0,"lap_time":0.0,
     "lap_times":[],"dnf":False,"dsq":False,"damage":0,"battery":100,"tyre_wear":0},
    {"name":"GAS","team":"Alpine","color":"#0090FF","pos":50,"lap":1,"distance":50,"speed":1.0,"lap_time":0.0,
     "lap_times":[],"dnf":False,"dsq":False,"damage":0,"battery":100,"tyre_wear":0},
    {"name":"DOO","team":"Alpine","color":"#0090FF","pos":55,"lap":1,"distance":55,"speed":1.0,"lap_time":0.0,
     "lap_times":[],"dnf":False,"dsq":False,"damage":0,"battery":100,"tyre_wear":0},
    {"name":"ALB","team":"Williams","color":"#005AFF","pos":60,"lap":1,"distance":60,"speed":1.0,"lap_time":0.0,
     "lap_times":[],"dnf":False,"dsq":False,"damage":0,"battery":100,"tyre_wear":0},
    {"name":"COL","team":"Williams","color":"#005AFF","pos":65,"lap":1,"distance":65,"speed":1.0,"lap_time":0.0,
     "lap_times":[],"dnf":False,"dsq":False,"damage":0,"battery":100,"tyre_wear":0},
    {"name":"HAD","team":"Racing Bulls","color":"#FF0000","pos":70,"lap":1,"distance":70,"speed":1.0,"lap_time":0.0,
     "lap_times":[],"dnf":False,"dsq":False,"damage":0,"battery":100,"tyre_wear":0},
    {"name":"LAW","team":"Racing Bulls","color":"#FF0000","pos":75,"lap":1,"distance":75,"speed":1.0,"lap_time":0.0,
     "lap_times":[],"dnf":False,"dsq":False,"damage":0,"battery":100,"tyre_wear":0},
    {"name":"HUL","team":"Sauber","color":"#E5E5E5","pos":80,"lap":1,"distance":80,"speed":1.0,"lap_time":0.0,
     "lap_times":[],"dnf":False,"dsq":False,"damage":0,"battery":100,"tyre_wear":0},
    {"name":"ZHO","team":"Sauber","color":"#E5E5E5","pos":85,"lap":1,"distance":85,"speed":1.0,"lap_time":0.0,
     "lap_times":[],"dnf":False,"dsq":False,"damage":0,"battery":100,"tyre_wear":0},
    {"name":"BEA","team":"Haas","color":"#FFFFFF","pos":90,"lap":1,"distance":90,"speed":1.0,"lap_time":0.0,
     "lap_times":[],"dnf":False,"dsq":False,"damage":0,"battery":100,"tyre_wear":0},
    {"name":"OCO","team":"Haas","color":"#FFFFFF","pos":95,"lap":1,"distance":95,"speed":1.0,"lap_time":0.0,
     "lap_times":[],"dnf":False,"dsq":False,"damage":0,"battery":100,"tyre_wear":0},
]

laps_total = st.sidebar.number_input("Totala varv", min_value=1, value=10)
tick_speed = 0.5  # sek per uppdatering
placeholder = st.empty()

# ----------------------
# Hjälpfunktion: sek -> min:sek:ms
# ----------------------
def format_time(seconds):
    minutes = int(seconds // 60)
    sec = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{minutes:02d}:{sec:02d}.{ms:03d}"

# ----------------------
# BOX-knapp
# ----------------------
if st.button("BOX!"):
    for d in drivers:
        if not d["dnf"] and not d["dsq"]:
            d["tyre_wear"] = 0
            d["damage"] = max(0, d["damage"] - random.uniform(0.5,2))
            d["battery"] = 100
    st.success("Pitstop utförd! Däck bytta ✅")

# ----------------------
# Incidenter, Safety Car och Röd flagg
# ----------------------
safety_car = False
red_flag = False

def random_incident(driver):
    global safety_car, red_flag
    r = random.random()
    if r < 0.015:  # 1.5% chans DNF
        driver["dnf"] = True
        return f"{driver['name']} bryter loppet (DNF)"
    elif r < 0.04:  # mindre incident
        driver["damage"] += random.uniform(1,3)
        if driver["damage"] > 10 and random.random() < 0.3:
            safety_car = True
        return f"{driver['name']} krockar lätt, skada +{driver['damage']:.1f}"
    return ""

# ----------------------
# Realtidsloop
# ----------------------
for tick in range(laps_total * track_length * 3):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=track_x, y=track_y, mode="lines", line=dict(color="black", width=4)))
    
    # Uppdatera bilar
    for d in drivers:
        if d["dnf"] or d["dsq"]:
            continue
        base_speed = random.uniform(0.8,1.2)
        # DRS-effekt: om inom 5 dist av framförvarande bil
        drivers_sorted = sorted(drivers, key=lambda x: x["lap"]*track_length + x["distance"], reverse=True)
        for i, drv in enumerate(drivers_sorted):
            if drv["name"] == d["name"] and i > 0:
                front = drivers_sorted[i-1]
                if (front["lap"]*track_length + front["distance"]) - (d["lap"]*track_length + d["distance"]) < 5:
                    base_speed *= 1.05  # DRS
        # Safety Car
        if safety_car:
            base_speed = 0.5
        # Röd flagg
        if red_flag:
            base_speed = 0
        d["speed"] = base_speed
        d["distance"] += d["speed"]
        d["lap_time"] += d["speed"] * 0.1
        d["tyre_wear"] = min(100, d["tyre_wear"] + 0.05)
        d["battery"] = max(0, d["battery"] - 0.1)
        
        # Varvkontroll
        if d["distance"] >= track_length:
            d["lap"] += 1
            d["lap_times"].append(d["lap_time"])
            d["lap_time"] = 0
            d["distance"] -= track_length
        
        msg = random_incident(d)
        if msg:
            st.warning(msg)
    
    # Slumpa röd flagg om Safety Car på länge
    if safety_car and random.random() < 0.01:
        red_flag = True
        safety_car = False
        st.error("Röd flagg! Lopp pausas 🚩")
    
    # Sortera leaderboard
    drivers_sorted = sorted(drivers, key=lambda x: x["lap"]*track_length + x["distance"], reverse=True)
    
    # Rita bilar
    for d in drivers_sorted:
        if d["dnf"] or d["dsq"]:
            continue
        fig.add_trace(go.Scatter(
            x=[track_x[int(d["distance"]) % track_length]],
            y=[track_y[int(d["distance"]) % track_length]],
            mode="markers+text",
            marker=dict(size=12, color=d["color"]),
            text=[f"{d['name']} {format_time(d['lap_time'])}\nTyre:{d['tyre_wear']:.0f}% Bat:{d['battery']:.0f}%"],
            textposition="top center"
        ))
    
    placeholder.plotly_chart(fig, use_container_width=True)
    time.sleep(tick_speed)
