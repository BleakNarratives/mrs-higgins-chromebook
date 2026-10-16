import os
import json
import time
import subprocess
from pathlib import Path

# Config
Higgins_Dir = Path.home() / "The-Werkz" / "Higgins" / "front_office_canonical"
SCOUT_QUEUE_DIR = Higgins_Dir / "scout_queue"
LOG_FILE = Higgins_Dir / "logs" / "agent_bus_bridge.log"

# Setup
os.makedirs(SCOUT_QUEUE_DIR, exist_ok=True)
os.makedirs(LOG_FILE.parent, exist_ok=True)

print(f"[*] Higgins AgentBus Bridge active. Watching {SCOUT_QUEUE_DIR}...")

def log(msg):
    with open(LOG_FILE, "a") as f:
        f.write(f"[{time.ctime()}] {msg}\n")
    print(msg)

# Simulate Agent Bus Emission (Stub for integration)
def emit_agent_bus_event(event_name, payload):
    log(f"EMITTING TO AGENT_BUS: {event_name} | Payload: {json.dumps(payload)}")
    # Placeholder for actual agent_bus.emit_event()
    # In production, this would be:
    # import sys; sys.path.insert(0, ...); import agent_bus; agent_bus.emit_event(...)

while True:
    files = [f for f in os.listdir(SCOUT_QUEUE_DIR) if f.endswith(".json")]
    for filename in files:
        filepath = SCOUT_QUEUE_DIR / filename
        log(f"Detected event: {filename}")
        
        try:
            with open(filepath, "r") as f:
                event_data = json.load(f)
            
            # THE TWIST: Instead of just subprocess, we bridge to orchestrator
            emit_agent_bus_event("higgins.scout_trigger", event_data)
            
            # Keep original functionality as fallback/verification
            log(f"Bridge trigger success. Moving to local execution for safety.")
            subprocess.run(["python3", "copywriter.py", "--platform", "Nostr", "--packages-dir", "./saas_packages"])
            
            os.remove(filepath)
            log(f"Successfully processed and cleaned: {filename}")
        except Exception as e:
            log(f"ERROR processing {filename}: {e}")
            
    time.sleep(2)
