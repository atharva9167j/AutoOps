import streamlit as st
import pandas as pd
import time
import state_manager 

st.set_page_config(page_title="AutoOps Dashboard", layout="wide")

st.title("🚀 AutoOps Dashboard")
st.caption("Autonomous System Healing & Predictive Scaling powered by Gemini")

# Polling Loop
placeholder = st.empty()

while True:
    state = state_manager.load_state()
    
    with placeholder.container():
        # Top Metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("Cluster Status")
            containers = state.get("containers", [])
            st.metric("Active Nodes", len(containers))
            for c in containers:
                st.success(f"Running: {c}")
                
        with col2:
            st.subheader("Oracle Prediction")
            pred = state.get("prediction", "STABLE")
            if pred == "STABLE":
                st.info("System Stable")
            else:
                st.error(f"⚠️ {pred}")
                st.markdown("Automatic Scaling Triggered")
                
        with col3:
            st.subheader("AI Actions (Last 5)")
            events = state.get("events", [])
            for e in events[:5]:
                icon = "🤖"
                if e['type'] == 'SCALE_UP': icon = "🚀"
                elif e['type'] == 'SCALE_DOWN': icon = "📉"
                elif e['type'] == 'DB_OPTIMIZATION': icon = "⚡"
                elif e['type'] == 'CRASH': icon = "🔥"
                
                st.markdown(f"**{e['time']} {icon} {e['type']}**")
                st.code(f"{e['message']}\n{e['details']}")

        # Charts
        st.subheader("Real-time Telemetry")
        
        history = state.get("cpu_history", [])
        if history:
            df = pd.DataFrame(history)
            
            tab1, tab2, tab3 = st.tabs(["CPU & Prediction", "Network I/O", "Disk Usage"])
            
            with tab1:
                st.caption("Actual (Blue) vs Oracle Predicted (Red)")
                # Streamlit line chart handles multiple columns automatically
                st.line_chart(df.set_index("time")[['cpu', 'predicted_cpu']])
            
            with tab2:
                st.caption("Network Traffic (KB/s)")
                st.line_chart(df.set_index("time")[['net_kb']])
                
            with tab3:
                st.caption("Disk I/O (IOPS)")
                st.line_chart(df.set_index("time")[['disk_io']])
        else:
            st.write("Waiting for data...")

    time.sleep(1)
