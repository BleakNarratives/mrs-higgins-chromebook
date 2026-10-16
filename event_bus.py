import os
import time
import subprocess

SCOUT_QUEUE_DIR = "./scout_queue"
os.makedirs(SCOUT_QUEUE_DIR, exist_ok=True)

print(f"[*] Watching {SCOUT_QUEUE_DIR} for incoming scout triggers...")

while True:
    files = [f for f in os.listdir(SCOUT_QUEUE_DIR) if f.endswith(".json")]
    for filename in files:
        filepath = os.path.join(SCOUT_QUEUE_DIR, filename)
        print(f"[!] New scout event detected: {filename}")
        
        # Trigger copywriter for Nostr platform
        subprocess.run(["python3", "copywriter.py", "--platform", "Nostr", "--packages-dir", "./saas_packages"])
        
        # Cleanup processed event
        os.remove(filepath)
    time.sleep(2)
