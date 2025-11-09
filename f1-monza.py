import streamlit as st
import plotly.graph_objects as go
import numpy as np
import random, time, threading
import speech_recognition as sr

# -----------------------
# 2025 Teams & Drivers
# -----------------------
teams_2025 = {
    "McLaren": {"color":"#FF8700", "drivers":[{"name":"Lando Norris","init":"NOR","number":4},
                                               {"name":"Oscar Piastri","init":"PIA","number":81}]},
    "Ferrari": {"color":"#DC0000", "drivers":[{"name":"Charles Leclerc","init":"LEC","number":16},
                                               {"name":"Carlos Sainz","init":"SAI","number":55}]},
    "Red Bull": {"color":"#1E5BC6", "drivers":[{"name":"Max Verstappen","init":"VER","number":1},
                                               {"name":"Sergio Pérez","init":"PER","number":11}]},
    "Mercedes": {"color":"#00D2BE", "drivers":[{"name":"Lewis Hamilton","init":"HAM","number":44},
                                               {"name":"George Russell","init":"RUS","number":63}]},
    "Alpine": {"color":"#0090FF", "drivers":[{"name":"Esteban Ocon","init":"OCO","number":31},
                                             {"name":"Pierre Gasly","init":"GAS","number":10}]},
    "Aston Martin": {"color":"#006F62", "drivers":[{"name":"Fernando Alonso","init":"ALO","number":14},
                                                   {"name":"Lance Stroll","init":"STR","number":18}]},
    "AlphaTauri": {"color":"#2B4562", "drivers":[{"name":"Yuki Tsunoda","init":"TSU","number":22},
                                                  {"name":"Nyck de Vries","init":"DEV","number":21}]},
    "Haas": {"color":"#FFFFFF", "drivers":[{"name":"Kevin Magnussen","init":"MAG","number":20},
                                           {"name":"Nico Hülkenberg","init":"HUL","number":27}]},
    "Alfa Romeo": {"color":"#900000", "drivers":[{"name":"Valtteri Bottas","init":"BOT","number":77},
                                                 {"name":"Zhou Guanyu","init":"ZHO","number":24}]},
    "Williams": {"color":"#005AFF", "drivers":[{"name":"Alex Albon","init":"ALB","number":23},
                                               {"name":"Logan Sargeant","init":"SAR","number":2}]}
}

# -----------------------
# Track: Monza
# -----------------------
monza_coords = [
    (0,0,0), (150,0,0), (250,50,0.5), (350,150,1), (400,300,2),
    (350,450,1.5), (250,550,1), (100,600,0.5), (0,650,0),
    (-100,600,-0.5), (-250,550,-1), (-350,450,-1.5), (-400,300,-2),
    (-350,150,-1), (-250,50,-0.5), (-150,0,0)
]
monza_sectors = [0.33,0.66,1.0]
lap_length_km = 5.3

# -----------------------
# Tyres & Car classes
# -----------------------
class Tyre:
    def __init__(self,name):
        self.name=name; self.wear=0; self.temp=80; self.pressure=22; self.punctured=False
    def step(self,speed,wear_rate,temp_adj,grip):
        if self.punctured: self.temp=max(20,self.temp-2); self.pressure=max(0,self.pressure-1.5); self.wear=min(100,self.wear+5)
        else: self.wear=min(100,self.wear+wear_rate*(speed/200)*grip); self.temp+=temp_adj; self.pressure=max(12,24-self.wear/6)

class Car:
    def __init__(self,driver_info,team_name,base_speed=200,base_rpm=11000):
        self.driver=driver_info; self.team=team_name; self.team_color=teams_2025[team_name]["color"]
        self.name=f"{driver_info['init']}"; self.number=driver_info["number"]
        self.base_speed=base_speed; self.base_rpm=base_rpm
        self.speed=base_speed; self.rpm=base_rpm; self.fuel=100; self.engine_health=100; self.front_wing_damage=0
        self.tyres={k:Tyre(k) for k in ["FL","FR","RL","RR"]}
        self.lap_progress=0.0; self.car_on_track_pos=0.0; self.lap_times=[]; self.sector_times=[]; self.best_lap=None
        self.pitstops=0; self.current_lap_start=time.time()
        self.last_sector=0
    def apply_event(self,event):
        t=event.get("type")
        if t=="puncture": self.tyres[event.get("tyre","RL")].punctured=True
        elif t=="front_wing": self.front_wing_damage=min(100,self.front_wing_damage+event.get("severity",20))
        elif t=="engine": self.engine_health=max(0,self.engine_health-event.get("severity",40))
    def step(self,dt,tyre_life_km,lap_length_km,weather_grip,weather_temp_adj,height_diff):
        fuel_burn=0.01+self.base_speed/50000; self.fuel=max(0,self.fuel-fuel_burn*dt)
        wear_per_km=100/tyre_life_km; km_in_dt=self.speed*dt/3600; base_wear_rate=wear_per_km*km_in_dt
        height_penalty=max(0,height_diff)*0.02; speed_penalty=height_penalty*50
        fw_penalty=self.front_wing_damage*0.03; engine_penalty=(100-self.engine_health)*0.02
        avg_wear=np.mean([t.wear for t in self.tyres.values()]); wear_penalty=max(0,(avg_wear-30)*0.03
)
        eff_speed=self.base_speed-fw_penalty-engine_penalty-wear_penalty-speed_penalty
        if self.fuel<10: eff_speed-=12
        self.speed=max(10,eff_speed+random.uniform(-3,3))
        self.rpm=max(1000,int(self.base_rpm*(self.speed/self.base_speed)*(1-(100-self.engine_health)/400)))
        for t in self.tyres.values(): t.step(self.speed,base_wear_rate,weather_temp_adj+height_penalty*5,weather_grip)
        if lap_length_km>0:
            seconds_per_lap=(lap_length_km/max(1e-3,self.speed))*3600; progress_inc=dt/seconds_per_lap
            self.lap_progress+=progress_inc
            # Sektorer
            for i,sec_end in enumerate(monza_sectors):
                if self.last_sector<i and self.lap_progress>=sec_end:
                    sector_time=time.time()-self.current_lap_start
                    self.sector_times.append(sector_time)
                    self.last_sector=i
            if self.lap_progress>=1.0:
                lap_time=time.time()-self.current_lap_start
                self.lap_times.append(lap_time)
                if self.best_lap is None or lap_time<self.best_lap: self.best_lap=lap_time
                self.current_lap_start=time.time(); self.lap_progress=self.lap_progress%1.0
                self.last_sector=0
            self.car_on_track_pos=self.lap_progress%1.0

class Rival(Car):
    def __init__(self,driver_info,team_name,base_speed=195,base_rpm=11000):
        super().__init__(driver_info,team_name,base_speed,base_rpm)
    def step_ai(self,dt,tyre_life_km,lap_length_km,weather_grip,weather_temp_adj,height_diff,rivals):
        super().step(dt,tyre_life_km,lap_length_km,weather_grip,weather_temp_adj,height_diff)
        if random.random()<0.004: self.tyres[random.choice(list(self.tyres.keys()))].punctured=True
        if random.random()<0.002: self.front_wing_damage=min(100,self.front_wing_damage+random.randint(10,25))
        if random.random()<0.001: self.engine_health=max(0,self.engine_health-random.randint(20,50))
        avg_wear=np.mean([t.wear for t in self.tyres.values()])
        if avg_wear>70 or self.fuel<15:
            self.pitstops+=1
            for t in self.tyres.values(): t.wear=0; t.punctured=False; t.temp=80
            self.front_wing_damage=max(0,self.front_wing_damage-10); self.fuel=100
            if random.random()<0.15:
                penalty=random.randint(5,15)
                st.session_state.event_log.insert(0,(time.strftime("%H:%M:%S"),f"🔧 {self.name} ({self.team}) – BAD PIT +{penalty}s"))
            else:
                st.session_state.event_log.insert(0,(time.strftime("%H:%M:%S"),f"⛽ {self.name} ({self.team}) – Pit Stop"))
        for other in rivals:
            if other==self: continue
            if abs(self.lap_progress-other.lap_progress)<0.02:
                if self.speed>other.speed or random.random()<0.3: self.lap_progress=other.lap_progress+0.001

# -----------------------
# Track helpers
# -----------------------
def interpolate_track(track_coords,t):
    n=len(track_coords); idx=int(t*(n-1)); next_idx=(idx+1)%n
    seg_t=t*(n-1)-idx; x=track_coords[idx][0]+seg_t*(track_coords[next_idx][0]-track_coords[idx][0])
    y=track_coords[idx][1]+seg_t*(track_coords[next_idx][1]-track_coords[idx][1])
    z=track_coords[idx][2]+seg_t*(track_coords[next_idx][2]-track_coords[idx][2])
    height_diff=track_coords[next_idx][2]-track_coords[idx][2]; return x,y,z,height_diff

def draw_track(car,rivals,track_coords):
    xs=[p[0] for p in track_coords]+[track_coords[0][0]]; ys=[p[1] for p in track_coords]+[track_coords[0][1]]
    fig=go.Figure(); fig.add_trace(go.Scatter(x=xs,y=ys,mode="lines",line=dict(color="gray",width=3)))
    px,py,pz,h_diff=interpolate_track(track_coords,car.car_on_track_pos)
    fig.add_trace(go.Scatter(x=[px],y=[py],mode="markers+text",marker=dict(size=12,color=car.team_color),text=[car.name],textposition="bottom center"))
    for r in rivals:
        rx,ry,rz,h_diff_r=interpolate_track(track_coords,r.lap_progress%1.0)
        fig.add_trace(go.Scatter(x=[rx],y=[ry],mode="markers+text",marker=dict(size=9,color=r.team_color),text=[r.name],textposition="bottom center",showlegend=False))
    fig.update_layout(height=500,margin=dict(l=10,r=10,t=30,b=10),showlegend=False)
    fig.update_xaxes(visible=False); fig.update_yaxes(visible=False); return fig

# -----------------------
# Voice pitstop
# -----------------------
def listen_for_box():
    recognizer=sr.Recognizer(); mic=sr.Microphone()
    with mic as source: recognizer.adjust_for_ambient_noise(source); audio=recognizer.listen(source,phrase_time_limit=3)
    try: text=recognizer.recognize_google(audio,language="sv-SE"); return "box box" in text.lower()
    except: return False

def voice_thread():
    while st.session_state.running:
        if listen_for_box():
            car=st.session_state.car
            car.pitstops+=1
            for t in car.tyres.values(): t.wear=0; t.punctured=False; t.temp=80
            car.front_wing_damage=0; car.engine_health=min(100,car.engine_health+20); car.fuel=100
            if random.random()<0.15:
                penalty=random.randint(5,15)
                st.session_state.event_log.insert(0,(time.strftime("%H:%M:%S"),f"🔧 {car.name} ({car.team}) – BAD PIT +{penalty}s"))
            else:
                st.session_state.event_log.insert(0,(time.strftime("%H:%M:%S"),"⛽ Pit Stop (Voice)"))

# -----------------------
# Streamlit UI
# -----------------------
st.set_page_config(page_title="F1 Monza Simulator - McLaren",layout="wide")
st.title("🏎️ F1 Simulator — Monza (McLaren)")

# Sidebar
st.sidebar.header("Race Settings")
laps=st.sidebar.number_input("Varv",1,200,20)
tyre_life_km=st.sidebar.number_input("Däcklivslängd km",10,1000,120)
tick_interval=st.sidebar.number_input("Uppdateringsintervall (sek)",0.1,5.0,1.0)
st.sidebar.header("Car Selection")
driver_choice=st.sidebar.selectbox("McLaren Föraren",["Lando Norris","Oscar Piastri"])
st.sidebar.header("Race Control")
start_btn=st.sidebar.button("▶ Start Race"); stop_btn=st.sidebar.button("⏸ Stop Race")

# -----------------------
# Session state
# -----------------------
if 'car' not in st.session_state:
    driver_info=[d for d in teams_2025["McLaren"]["drivers"] if d["name"]==driver_choice][0]
    st.session_state.car=Car(driver_info,"McLaren",base_speed=200)
    rivals=[]
    for team_name,team_data in teams_2025.items():
        if team_name=="McLaren": continue
        for driver in team_data["drivers"]:
            rivals.append(Rival(driver,team_name,base_speed=195*random.uniform(0.95,1.05)))
    st.session_state.rivals=rivals; st.session_state.running=False; st.session_state.event_log=[]

# Start/Stop race loop
def race_loop():
    dt = tick_interval
    car = st.session_state.car
    rivals = st.session_state.rivals
    while st.session_state.running:
        height_diff = 0
        car.step(dt,tyre_life_km,lap_length_km,weather_grip=1.0,weather_temp_adj=0,height_diff=height_diff)
        for r in rivals: r.step_ai(dt,tyre_life_km,lap_length_km,weather_grip=1.0,weather_temp_adj=0,height_diff=height_diff,rivals=rivals)
        time.sleep(dt)

if start_btn: st.session_state.running=True; threading.Thread(target=voice_thread,daemon=True).start()
if stop_btn: st.session_state.running=False
if st.session_state.running and 'race_thread' not in st.session_state:
    st.session_state.race_thread=threading.Thread(target=race_loop,daemon=True); st.session_state.race_thread.start()

# -----------------------
# Display Track & Telemetry
# -----------------------
st.subheader("Track Map"); st.plotly_chart(draw_track(st.session_state.car,st.session_state.rivals,monza_coords),use_container_width=True)

car=st.session_state.car
st.subheader("Telemetry")
st.write(f"Speed: {car.speed:.1f} km/h | RPM: {car.rpm} | Fuel: {car.fuel:.1f}% | Engine: {car.engine_health:.1f} | Front Wing: {car.front_wing_damage:.1f}")
st.write("Tyres:"); st.write({k:f"Wear: {v.wear:.1f} Temp:{v.temp:.1f}" for k,v in car.tyres.items()})

# -----------------------
# Leaderboard
# -----------------------
st.subheader("🏁 Leaderboard")
all_cars = [st.session_state.car] + st.session_state.rivals
all_cars_sorted = sorted(all_cars, key=lambda x: (len(x.lap_times), x.lap_progress), reverse=True)
leaderboard=[]
for i,c in enumerate(all_cars_sorted,1):
    sector = (np.searchsorted(monza_sectors, c.lap_progress)+1)
    bestlap = f"{c.best_lap:.1f}" if c.best_lap else "-"
    leaderboard.append({
        "Pos": i, "Driver": f"{c.name} ({c.team})", "Lap": len(c.lap_times), "BestLap": bestlap,
        "Sector": sector, "Tyre": list(c.tyres.values())[0].name, "Pitstops": c.pitstops
    })
st.table(leaderboard)

# -----------------------
# Event log
# -----------------------
st.subheader("Event Log")
st.text("\n".join([f"[{t}] {msg}" for t,msg in st.session_state.event_log]))
