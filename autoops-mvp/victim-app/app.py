from flask import Flask, request
import sqlite3
import time
import os

app = Flask(__name__)
DB_PATH = 'prod.db'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    return {"status": "running", "container": os.environ.get("HOSTNAME", "unknown")}

@app.route('/search')
def search():
    query = request.args.get('name', '')
    conn = get_db_connection()
    # SIMULATE SLOW QUERY: No index on 'name'
    # We use a LIKE query with wildcards to ensure it's slow if the string is long or DB is large
    start_time = time.time()
    
    # BURN CPU: Calculate large factorials to force CPU usage up
    x = 0
    for i in range(500000): 
        x += i * i

    res = conn.execute(f"SELECT * FROM users WHERE name LIKE '%{query}%'").fetchall()
    duration = time.time() - start_time
    if duration > 0.5:
        print(f"SLOW_QUERY: {duration:.4f}s for query '{query}'")
    conn.close()
    return {"count": len(res), "duration": duration}

@app.route('/leak')
def leak():
    # SIMULATE MEMORY LEAK: Appends to a global list until OOM
    global memory_hog
    memory_hog = getattr(app, 'memory_hog', [])
    # Append a large string to memory
    memory_hog.extend(["data" * 100000] * 100) # ~10MB per call roughly?
    app.memory_hog = memory_hog
    return {"status": "leaking", "memory_hog_chunks": len(memory_hog)}

if __name__ == '__main__':
    # Initialize DB if not exists (simple check)
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)")
        # Seed some data to make search actually work a bit
        conn.execute("INSERT INTO users (name) VALUES ('Alice'), ('Bob'), ('Charlie')")
        for i in range(1000):
            conn.execute(f"INSERT INTO users (name) VALUES ('User_{i}')")
        conn.commit()
        conn.close()
        
    app.run(host='0.0.0.0', port=5000)
