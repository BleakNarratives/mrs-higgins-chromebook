#!/usr/bin/env python3
"""Kindred bus listener — Mrs. Higgins front-office sidecar.

Watches the RootBase gossip bus ledger (~/.warden/gossip_bus/messages.jsonl)
for kindred events and reacts like a front office should: logs the traffic,
keeps a routing log, and files a rumor when a companion ships something.

Run:  python3 higgins_kindred_listener.py [--once]
Stop: Ctrl+C

DNA_TAG: ORIGIN=BleakNarratives/Higgins | ROLE=kindred-bus-listener | LAST_SYNC=2026-08-29
"""

from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

GOSSIP_LEDGER = Path.home() / ".warden" / "gossip_bus" / "messages.jsonl"
ROUTING_LOG = Path(__file__).parent / "logs" / "kindred_events.jsonl"
POSITION_FILE = Path(__file__).parent / "state" / "kindred_listener_position"


def load_position() -> int:
    try:
        return int(POSITION_FILE.read_text().strip())
    except Exception:
        return 0


def save_position(offset: int) -> None:
    POSITION_FILE.parent.mkdir(parents=True, exist_ok=True)
    POSITION_FILE.write_text(str(offset))


def read_new_events(offset: int) -> tuple[List[Dict[str, Any]], int]:
    """Read new gossip entries from offset. Returns (events, new_offset)."""
    try:
        size = GOSSIP_LEDGER.stat().st_size
    except OSError:
        return [], offset
    if size < offset:  # ledger rotated/truncated
        offset = 0
    if size == offset:
        return [], offset
    events: List[Dict[str, Any]] = []
    with open(GOSSIP_LEDGER, "r", encoding="utf-8") as f:
        f.seek(offset)
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return events, size


def handle_event(event: Dict[str, Any]) -> Optional[str]:
    """Return a one-line front-office note for a kindred event, else None."""
    payload = event.get("payload") or {}
    if not str(event.get("channel", "")).startswith("governance.gossip"):
        return None
    if event.get("sender_id") != "kindred":
        return None
    inner = payload.get("payload") or {}
    headline = inner.get("headline") or payload.get("event_type") or "kindred event"
    detail = inner.get("detail") or ""
    return f"{headline}" + (f" — {detail}" if detail else "")


def log_event(note: str, raw: Dict[str, Any]) -> None:
    ROUTING_LOG.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "note": note,
        "message_id": raw.get("message_id"),
    }
    with open(ROUTING_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def main() -> None:
    ap = argparse.ArgumentParser(description="Mrs. Higgins — Kindred bus listener")
    ap.add_argument("--once", action="store_true", help="process pending events once and exit")
    args = ap.parse_args()

    offset = load_position()
    print(f"[*] Higgins listening for kindred events on {GOSSIP_LEDGER}")

    if args.once:
        events, new_offset = read_new_events(offset)
        for ev in events:
            note = handle_event(ev)
            if note:
                log_event(note, ev)
                print(f"[kindred] {note}")
        save_position(new_offset)
        print(f"[*] Processed {len(events)} events; position saved.")
        return

    while True:
        events, new_offset = read_new_events(offset)
        for ev in events:
            note = handle_event(ev)
            if note:
                log_event(note, ev)
                print(f"[kindred] {note}", flush=True)
        offset = new_offset
        save_position(offset)
        time.sleep(5)


if __name__ == "__main__":
    main()
