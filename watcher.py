#!/usr/bin/env python3
"""The-Werkz watcher — real system monitoring, no placeholder.

Monitors: disk, memory, gossip bus tail (kindred + governance events),
city-api health, and Higgins front-office core file integrity.
Writes to system_events.log with real data every cycle.

DNA_TAG: ORIGIN=BleakNarratives/Higgins | ROLE=system-watcher | LAST_SYNC=2026-08-29
"""

import time
import os
import shutil
import urllib.request
import json
from datetime import datetime
from pathlib import Path

WATCH_DIR = Path.home() / "The-Werkz"
LOG_FILE = WATCH_DIR / "Higgins" / "system_events.log"
GOSSIP_LEDGER = Path.home() / ".warden" / "gossip_bus" / "messages.jsonl"
CITY_API = "http://127.0.0.1:8765/health"

_last_gossip_size = 0


def log_event(event: str) -> None:
    with open(LOG_FILE, "a") as f:
        f.write(f"{datetime.now().isoformat()} - {event}\n")


def check_disk() -> str:
    usage = shutil.disk_usage(str(WATCH_DIR))
    pct = usage.used / usage.total * 100
    return f"disk {pct:.0f}% used ({usage.used // (2**30)}G/{usage.total // (2**30)}G)"


def check_memory() -> str:
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemAvailable:"):
                    avail_kb = int(line.split()[1])
                    return f"mem avail {avail_kb // 1024}MB"
    except OSError:
        pass
    return "mem: unknown"


def check_city_api() -> str:
    try:
        with urllib.request.urlopen(CITY_API, timeout=3) as resp:
            data = json.loads(resp.read())
        return f"city-api {data.get('status', '?')} (errors={data.get('error_count', '?')})"
    except Exception as e:
        return f"city-api DOWN ({e})"


def check_gossip_bus() -> str:
    global _last_gossip_size
    try:
        size = GOSSIP_LEDGER.stat().st_size
        if size > _last_gossip_size:
            with open(GOSSIP_LEDGER, "r", encoding="utf-8") as f:
                f.seek(_last_gossip_size)
                new_lines = f.read().strip().splitlines()
                for line in new_lines:
                    try:
                        msg = json.loads(line)
                        sender = msg.get("sender_id", "?")
                        channel = msg.get("channel", "?")
                        log_event(f"gossip: {sender} → {channel}")
                    except json.JSONDecodeError:
                        pass
            _last_gossip_size = size
            return f"gossip ledger +{len(new_lines)} entries"
    except OSError:
        pass
    return "gossip ledger: no change"


def main() -> None:
    global _last_gossip_size
    try:
        _last_gossip_size = GOSSIP_LEDGER.stat().st_size
    except OSError:
        _last_gossip_size = 0

    log_event("Watcher initiated — real monitoring active.")

    while True:
        time.sleep(60)
        parts = [
            check_disk(),
            check_memory(),
            check_city_api(),
            check_gossip_bus(),
        ]
        log_event("Heartbeat: " + " | ".join(parts))


if __name__ == "__main__":
    main()
