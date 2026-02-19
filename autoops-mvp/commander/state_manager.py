import json
import os
import time

STATE_FILE = "system_state.json"

def init_state():
    if not os.path.exists(STATE_FILE):
        val = {
            "containers": [],
            "cpu_history": [],
            "events": [],
            "prediction": "STABLE"
        }
        with open(STATE_FILE, "w") as f:
            json.dump(val, f)

def load_state():
    try:
        if not os.path.exists(STATE_FILE):
            init_state()
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except:
        return {"containers": [], "cpu_history": [], "events": [], "prediction": "STABLE"}

def save_state(state):
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(state, f)
    except Exception as e:
        print(f"Error saving state: {e}")

def log_event(event_type, message, details=""):
    state = load_state()
    event = {
        "time": time.strftime("%H:%M:%S"),
        "type": event_type,
        "message": message,
        "details": details
    }
    # Keep last 50 events
    state["events"].insert(0, event)
    state["events"] = state["events"][:50]
    save_state(state)

def update_metrics(cpu_pct, predicted_cpu, prediction, containers, net_kb=0, disk_io=0):
    state = load_state()
    state["prediction"] = prediction
    state["containers"] = containers
    
    # Add history point
    state["cpu_history"].append({
        "time": time.strftime("%H:%M:%S"),
        "cpu": cpu_pct,
        "predicted_cpu": predicted_cpu,
        "net_kb": net_kb,
        "disk_io": disk_io
    })
    # Keep last 40 points (Fixed window as requested)
    state["cpu_history"] = state["cpu_history"][-40:]
    
    save_state(state)
