import requests
import time
import threading
import random

TARGET_URL = "http://localhost:5000"

request_count = 0

def report_stats():
    global request_count
    while True:
        time.sleep(1)
        if request_count > 0:
            print(f"\r[Traffic Gen] Requests sent in last 1s: {request_count}   ", end="")
            request_count = 0



attack_intensity = 0 # 0 = Idle, 1-10 = Intensity
threads = []

def simulate_search_traffic():
    global request_count
    while True:
        try:
            # Random query
            q = random.choice(['ice', 'bob', 'a', 'test', 'data', 'user'])
            resp = requests.get(f"{TARGET_URL}/search?name={q}")
            request_count += 1
        except Exception as e:
            pass
        # Sleep varies by thread, but we control number of threads
        time.sleep(random.uniform(0.05, 0.2))

def verify_threads():
    global threads
    # Manage threads based on intensity
    # Target threads = intensity * 2
    target_threads = attack_intensity * 2
    
    current_count = len([t for t in threads if t.is_alive()])
    
    if current_count < target_threads:
        # Add threads
        for _ in range(target_threads - current_count):
            t = threading.Thread(target=simulate_search_traffic)
            t.daemon = True
            t.start()
            threads.append(t)
    elif current_count > target_threads:
        # We can't easily kill threads in Python without flags, 
        # but for this MVP, "Reducing" means we just reset or let them die if we used flags.
        # Simplification: We'll just set a global "active_limit" or similar?
        # Actually simplest way for MVP: Just ignore reducing threads gracefully, 
        # or restart the whole set. 
        # Better: Implementation with a check inside the loop.
        pass

def trigger_leak():
    print("Triggering Memory Leak...")
    try:
        resp = requests.get(f"{TARGET_URL}/leak")
        print(f"Leak Trigger: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"Leak Error: {e}")

def attack_loop_check():
    # Workers check this index
    pass
    
# redone worker for better control
def smart_worker(worker_id):
    global request_count, attack_intensity
    while True:
        # If this worker ID is > intensity * 2, sleep/idle
        if worker_id > attack_intensity * 2:
            time.sleep(1)
            continue
            
        try:
            q = random.choice(['ice', 'bob', 'a', 'test', 'data', 'user'])
            resp = requests.get(f"{TARGET_URL}/search?name={q}")
            request_count += 1
        except:
            pass
        time.sleep(random.uniform(0.05, 0.2))

# Initialize pool of 20 threads (Max intensity 10 * 2)
def init_pool():
    for i in range(1, 21):
        t = threading.Thread(target=smart_worker, args=(i,), daemon=True)
        t.start()

if __name__ == "__main__":
    print("🔥 Chaos Monkey Started")
    
    # Start reporter thread
    threading.Thread(target=report_stats, daemon=True).start()
    
    # Init Worker Pool
    init_pool()
    
    while True:
        print(f"\nStatus: Intensity Level {attack_intensity}/10")
        print("Options:")
        print("1. Increase Traffic (+)")
        print("2. Decrease Traffic (-)")
        print("3. Trigger OOM (Memory Leak)")
        print("4. Exit")
        choice = input("Select: ")
        
        if choice == '1':
            if attack_intensity < 10:
                attack_intensity += 1
                print(f"🚀 Increasing Intensity to {attack_intensity}")
            else:
                print("MAX POWER REACHED!")
        elif choice == '2':
            if attack_intensity > 0:
                attack_intensity -= 1
                print(f"mb📉 Decreasing Intensity to {attack_intensity}")
            else:
                print("Already IDLE.")
        elif choice == '3':
            trigger_leak()
        elif choice == '4':
            break
