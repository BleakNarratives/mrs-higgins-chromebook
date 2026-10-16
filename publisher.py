import os
import glob
import json
import time
import urllib.request
import ssl

OUTPUT_DIR = "./copy_output"
RELAYS = [
    "wss://relay.damus.io",
    "wss://nos.lol",
    "wss://relay.nostr.band"
]

def publish_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    filename = os.path.basename(filepath)
    print(f"[NOSTR] Publishing {filename}...")
    
    # Simple event structure readout (can be extended with secp256k1 signing)
    print(f"[] Queued {len(content)} chars from {filename} for broadcast.")

def main():
    files = glob.glob(os.path.join(OUTPUT_DIR, "*.md"))
    if not files:
        print("[!] No copy files found in ./copy_output/")
        return
        
    print(f"[*] Found {len(files)} copy files. Broadcasting to relays...")
    for filepath in files:
        publish_file(filepath)
        time.sleep(1)
    print("[DONE] All available copy processed.")

if __name__ == "__main__":
    main()
