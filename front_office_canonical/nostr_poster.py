#!/usr/bin/env python3
"""
nostr_poster.py — actually posts to Nostr relays.
Uses schnorr.py for signing. Reads nsec from vault.
"""
# [DNA_TAG]
# ORIGIN: Crostini-Chromebook (auto-detected)
# PILLAR: rootbase-engine-room
# DEPS: schnorr
# ROLE: Component of UNPACKED
# AUTHOR: Auto-tagged by Buffy (DNA Sweeper)
# SESSION: 2026-08-22 ShipWreckD OS Builder
# TIER: Recruit (5)
# AKA: nostr_poster, MrsHiggins_Unified-module
# [/DNA_TAG]

import json, time, hashlib, ssl, asyncio, websockets, os
from pathlib import Path

sys_path_insert = str(Path(__file__).parent)
import sys; sys.path.insert(0, sys_path_insert)
from schnorr import schnorr_sign

RELAYS = [
    "wss://relay.damus.io",
    "wss://nos.lol",
    "wss://relay.primal.net",
    
]

VAULT_KEY = Path("/storage/emulated/0/RootBase/vault/keys/nostr.key")

def load_privkey() -> str:
    key = os.getenv("NOSTR_PRIVATE_KEY", "")
    if not key and VAULT_KEY.exists():
        key = VAULT_KEY.read_text().strip()
    if not key:
        raise ValueError("No Nostr private key found in vault or NOSTR_PRIVATE_KEY env")
    # strip nsec prefix if present — we need raw hex
    if key.startswith("nsec"):
        try:
            from bech32 import bech32_decode, convertbits
            _, data = bech32_decode(key)
            key = bytes(convertbits(data, 5, 8, False)).hex()
        except ImportError:
            raise ValueError("nsec key provided but bech32 not installed — store raw hex key instead")
    return key

def pubkey_from_privkey(priv_hex: str) -> str:
    from schnorr import point_mul, G
    P = point_mul(int(priv_hex, 16), G)
    return hex(P[0])[2:].zfill(64)

def make_event(priv_hex: str, content: str, kind: int = 1) -> dict:
    pub = pubkey_from_privkey(priv_hex)
    created_at = int(time.time())
    tags = [["t", "ai"], ["t", "buildinpublic"], ["t", "nostr"], ["t", "bitcoin"]]
    
    # normalize content to avoid unicode encoding mismatches
    content = content.replace("\u2019", "'").replace("\u2014", "-").replace("\u2013", "-")
    serialized = json.dumps([0, pub, created_at, kind, tags, content], separators=(',', ':'), ensure_ascii=False)
    event_id = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
    sig = schnorr_sign(event_id, priv_hex)
    
    return {
        "id": event_id,
        "pubkey": pub,
        "created_at": created_at,
        "kind": kind,
        "tags": tags,
        "content": content,
        "sig": sig,
    }

async def send_to_relay(relay_url: str, event: dict, timeout: int = 8) -> bool:
    try:
        ssl_ctx = ssl.create_default_context()
        async with websockets.connect(relay_url, ssl=ssl_ctx, open_timeout=timeout) as ws:
            msg = json.dumps(["EVENT", event])
            await ws.send(msg)
            resp = await asyncio.wait_for(ws.recv(), timeout=timeout)
            data = json.loads(resp)
            if data[0] == "OK" and data[2]:
                print(f"  [OK] {relay_url}")
                return True
            else:
                print(f"  [FAIL] {relay_url}: {data}")
                return False
    except Exception as e:
        print(f"  [ERR] {relay_url}: {e}")
        return False

async def post(content: str) -> int:
    priv_hex = load_privkey()
    event = make_event(priv_hex, content)
    print(f"  Event ID: {event['id'][:16]}...")
    tasks = [send_to_relay(r, event) for r in RELAYS]
    results = await asyncio.gather(*tasks)
    return sum(results)

def post_note(content: str) -> int:
    return asyncio.run(post(content))

if __name__ == "__main__":
    import sys
    content = sys.argv[1] if len(sys.argv) > 1 else "Test post from Higgins — BleakNarratives swarm is live."
    hits = post_note(content)
    print(f"\n  Posted to {hits}/{len(RELAYS)} relays")
