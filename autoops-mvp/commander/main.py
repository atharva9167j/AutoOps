import state_manager 
import docker
import google.generativeai as genai
from oracle import MockOracle
import time
import os
import random

# Configuration
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyCd7it3779r_TC68CSy4X1d4O2Z-4Iadr4")
VICTIM_IMAGE_NAME = "victim-app"
NETWORK_NAME = "autoops-net"

# Initialize
try:
    client = docker.from_env()
except Exception as e:
    print(f"Error connecting to Docker: {e}")
    client = None

if GEMINI_API_KEY != "YOUR_GEMINI_API_KEY_HERE":
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-3-flash-preview')
else:
    print("Warning: Gemini API Key not set.")
    model = None

oracle = MockOracle()

# Initialize & Reset State (Clear old schema data)
if os.path.exists("system_state.json"):
    os.remove("system_state.json")
state_manager.init_state()

def heal_system(container, error_log):
    print(f"🚨 Analyzing Error: {error_log}")
    
    if not model:
        print("❌ AI Model not configured. Cannot heal.")
        state_manager.log_event("AI_ERROR", "Gemini not configured", "Skipping fix.")
        return

    prompt = f"System Error Log: {error_log}. Provide a shell command to fix this or a SQL command to optimize the SQLite DB (file is prod.db). Return ONLY the command text, no markdown."
    try:
        state_manager.log_event("AI_ANALYSIS", "Gemini Analyzing Log", error_log[:100]+"...")
        response = model.generate_content(prompt)
        fix_command = response.text.strip()
        
        # Execute fix in the container
        print(f"🛠️ Applying Fix: {fix_command}")
        # Clean up command if it has quotes or markdown
        fix_command = fix_command.replace('```sql', '').replace('```sh', '').replace('```', '').strip()
        
        # Determine fix type for dashboard
        fix_type = "DB_OPTIMIZATION" if "sqlite" in fix_command.lower() or "index" in fix_command.lower() else "SYSTEM_FIX"
        
        if "CREATE INDEX" in fix_command.upper() and not fix_command.startswith("sqlite3"):
            fix_command = f'sqlite3 prod.db "{fix_command}"'
            
        exec_start_time = time.time()
        res = container.exec_run(fix_command)
        duration = time.time() - exec_start_time
        
        msg = f"Executed: {fix_command}"
        state_manager.log_event(fix_type, f"AI Auto-Healed {container.name}", msg)
        print(f"   Result: {res.exit_code} - {res.output.decode()}")
        
    except Exception as e:
        print(f"Error during healing: {e}")
        state_manager.log_event("ERROR", "Healing Failed", str(e))

def monitor_loop():
    if not client: return

    print("Subscribing to Docker stats...")
    state_manager.log_event("SYSTEM", "Commander Started", "Monitoring cluster...")
    
    # Ensure network exists
    try:
        client.networks.get(NETWORK_NAME)
    except docker.errors.NotFound:
        client.networks.create(NETWORK_NAME)

    while True:
        try:
            # 1. Check Metrics for active victim containers
            containers = client.containers.list(filters={"ancestor": VICTIM_IMAGE_NAME})
            active_names = [c.name for c in containers]
            
            # Simple avg CPU for cluster
            total_cpu = 0
            container_count = len(containers)
            
            if not containers:
                print("No victim containers found.")
            
            for container in containers:
                try:
                    stats = container.stats(stream=False)
                    # Simple CPU calc
                    cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - stats['precpu_stats']['cpu_usage']['total_usage']
                    system_cpu_delta = stats['cpu_stats']['system_cpu_usage'] - stats['precpu_stats']['system_cpu_usage']
                    
                    if system_cpu_delta > 0:
                        cpu_pct = (cpu_delta / system_cpu_delta) * stats['cpu_stats']['online_cpus'] * 100
                    else:
                        cpu_pct = 0.0
                    
                    total_cpu += cpu_pct

                    # 2b. Check Logs for Application Errors (Slow Queries)
                    logs = container.logs(since=int(time.time())-5).decode()
                    if "SLOW_QUERY" in logs:
                        print(f"⚠️ Slow Query Detected in {container.name}!")
                        heal_system(container, f"Application Log showing slow query: {logs}")
                        
                except Exception as e:
                    pass
            
            # Cluster Average CPU
            avg_cpu = total_cpu / container_count if container_count > 0 else 0
            
            # 2. Oracle Prediction (Returns tuple now)
            prediction, predicted_val = oracle.predict(avg_cpu)
            print(f"Cluster CPU: {avg_cpu:.2f}% | Pred: {predicted_val:.2f} | Status: {prediction}")
            
            # Mock Network/Disk Stats (Since obtaining real ones from Docker SDK on Windows is flaky)
            # Make them correlated with CPU for realism
            mock_net = (avg_cpu * 10) + random.randint(0, 50) # KB/s
            mock_disk = (avg_cpu * 2) + random.randint(0, 10) # IOPS
            
            # Update Shared State for Dashboard
            state_manager.update_metrics(avg_cpu, predicted_val, prediction, active_names, mock_net, mock_disk)

            # SCALING LOGIC
            replicas = client.containers.list(filters={"name": "replica"})
            
            # A. SCALE UP
            if prediction == "CRITICAL_SPIKE_PREDICTED" and len(replicas) < 3:
                # Add delay or check if we just scaled? For MVP, immediate is fine.
                print("🚀 Scaling up: Launching replica...")
                new_name = f"replica-{int(time.time())}"
                client.containers.run(
                    VICTIM_IMAGE_NAME, 
                    detach=True, 
                    name=new_name, 
                    mem_limit="128m",
                    network=NETWORK_NAME,
                    environment={"HOSTNAME": "replica"} # Simple hostname
                )
                state_manager.log_event("SCALE_UP", "Oracle Predicted Spike", f"Launched {new_name}")

            # B. SCALE DOWN (If CPU is low and we have replicas)
            # Adjusted threshold to be slightly stickier
            elif avg_cpu < 5.0 and len(replicas) > 0 and prediction == "STABLE":
                # Remove one replica
                target = replicas[0]
                print(f"📉 Scaling down: Removing {target.name}...")
                target.stop()
                target.remove()
                state_manager.log_event("SCALE_DOWN", "Low Traffic Detected", f"Removed {target.name}")

            # 3. Check for crashed containers (OOM)
            # We must use all=True to find exited ones!
            exited_containers = client.containers.list(all=True, filters={"ancestor": VICTIM_IMAGE_NAME, "status": "exited"})
            for container in exited_containers:
                container.reload() # Refresh state
                exit_code = container.attrs['State']['ExitCode']
                # Docker Exit Code 137 = OOM (kill -9)
                if exit_code == 137:
                    print(f"Container {container.name} crashed (OOM).")
                    
                    # Prevent infinite loop of fixing the same dead container:
                    # Check if we already fixed this exact container ID recently? 
                    # For MVP, we'll just restart it and log.
                    
                    logs = container.logs(tail=20).decode()
                    state_manager.log_event("CRASH", f"{container.name} OOM Killed", "Triggering RCA...")
                    heal_system(container, f"Container crashed with Exit {exit_code}. Last logs: {logs}")
                    
                    # Auto-restart for demo continuity
                    print(f"♻️ Restarting {container.name}...")
                    container.start()
                    state_manager.log_event("SYSTEM_FIX", "Auto-Restarted Container", container.name)

        except Exception as e:
            print(f"Monitor Loop Error: {e}")
        
        time.sleep(1)

if __name__ == "__main__":
    monitor_loop()
