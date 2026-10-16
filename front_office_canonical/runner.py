import subprocess

def run_pipeline():
    print("\n=== BROADCASTING COPY TO NOSTR ===")
    subprocess.run(["python3", "publisher.py"])

if __name__ == "__main__":
    run_pipeline()
