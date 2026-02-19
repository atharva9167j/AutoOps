# 🤖 AutoOps MVP: Autonomous System Healing Demo

**AutoOps** demonstrates the future of Site Reliability Engineering (SRE) â€“ where AI agents autonomously detect, predict, and fix production issues in real-time.

![Status](https://img.shields.io/badge/Status-Running-green) ![Docker](https://img.shields.io/badge/Docker-Required-blue) ![Python](https://img.shields.io/badge/Python-3.9%2B-yellow)

---

## 🚀 Features

This demo simulates a production environment (`Victim App`) under attack (`Chaos Monkey`) and shows how the `Commander` (AI Orchestrator) saves the day.

### 1. **Predictive Scaling (The Oracle)**
- **Problem**: Sudden traffic spikes crash servers.
- **Solution**: The **Oracle** analyzes CPU trends. If a "Critical Spike" is predicted, it **pre-emptively scales up** replicas before the crash happens.
- **Dashboard**: Visualizes "Actual vs Predicted" CPU load in real-time.

### 2. **Auto-RCA & Healing (OOM Crash)**
- **Problem**: Memory leaks cause containers to crash (Exit Code 137).
- **Solution**: Commander detects the crash, grabs the logs, sends them to **Gemini**, and identifies the root cause. (It then restarts the container to keep the demo alive).

### 3. **Self-Optimizing Databases (Slow Queries)**
- **Problem**: Inefficient SQL queries slow down the app.
- **Solution**: Commander listens for `SLOW_QUERY` logs. It uses Gemini to analyze the query and **automatically applies a fix** (e.g., `CREATE INDEX`) to the live database.

---

## 🛠️ Components

| Component | Description | Tech Stack |
| :--- | :--- | :--- |
| **Victim App** | Flask App with hidden bugs (Memory Leak, Slow Query). | Python, Docker, SQLite |
| **Chaos Monkey** | Attack tool to simulate traffic & trigger bugs. | Python (Multi-threaded) |
| **Commander** | The "Brain". Monitors Docker, predicts trends, heals app. | Python, Docker SDK, Gemini |
| **Dashboard** | Real-time mission control UI. | Streamlit, Pandas |

---

## 🚦 How to Run

### Prerequisites
1.  **Docker Desktop** (Must be running).
2.  **Python 3.9+**.
3.  **Gemini API Key**.

### One-Click Demo
1.  **Clone/Open** the `autoops-mvp` folder.
2.  **Set your API Key** (Optional but recommended for AI features):
    *   Open `commander/main.py`.
    *   Replace `GEMINI_API_KEY` value or set it as an environment variable.
3.  **Run the script**:
    ```powershell
    .\run_demo.bat
    ```

### Manual Setup (If script fails)
1.  **Install Deps**: `pip install -r requirements.txt` (inside `.venv`).
2.  **Build Image**: `cd victim-app && docker build -t victim-app .`
3.  **Run Commander**: `python commander/main.py`
4.  **Run Dashboard**: `streamlit run commander/dashboard.py`
5.  **Run Chaos**: `python chaos/attack.py`

---

## 🎮 Interactive Scenarios

### Scenario A: The Traffic Spike (Scaling)
1.  Go to **Chaos Monkey** window.
2.  Select **Option 1 (Increase Traffic)**. Press it 3-5 times to ramp up load.
3.  **Watch Dashboard**: 
    *   CPU (Blue) rises. Prediction (Red) spikes.
    *   Status changes to **CRITICAL SPIKE PREDICTED**.
    *   **Action**: "🚀 SCALE_UP" event appears. New containers launch.
4.  Select **Option 2 (Decrease Traffic)** to cool down. Watch "📉 SCALE_DOWN".

### Scenario B: The Fatal Crash (OOM)
1.  Go to **Chaos Monkey** window.
2.  Select **Option 3 (Trigger OOM)**.
3.  **Watch Dashboard**:
    *   One node turns RED or disappears.
    *   **Action**: "🔥 CRASH" event appears (OOM Killed).
    *   **Action**: "🤖 SYSTEM_FIX" appears (Auto-Restarted).

### Scenario C: The Slow Query (Db Optimization)
*(Happens naturally during high traffic or random queries)*
1.  Watch for **"⚡ DB_OPTIMIZATION"** in the AI Actions log.
2.  Commander detected a slow search and applied an index!

---

## 📂 Project Structure
```
autoops-mvp/
├── chaos/              # Attack tools
├── commander/          # AI Orchestrator & Dashboard
│   ├── main.py         # Logic
│   ├── dashboard.py    # UI
│   └── oracle.py       # Prediction Algo
├── victim-app/         # The buggy app
├── run_demo.bat        # Launcher
└── requirements.txt    # Deps
```

Made with ❤️ by the AutoOps Team.
