import json, time, hashlib, hmac, asyncio, websockets, os
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization

RELAYS = [
    "wss://relay.damus.io",
    "wss://relay.nostr.band",
    "wss://nos.lol",
    "wss://nostr.wine",
]

KEYS_FILE = "/storage/emulated/0/RootBase/mrs_higgins_saas/nostr_keys.json"
LOG_FILE  = "/storage/emulated/0/RootBase/mrs_higgins_saas/front_desk_routing_log.json"

def load_keys():
    with open(KEYS_FILE) as f:
        return json.load(f)

def sign_event(event_dict, priv_hex):
    priv_int = int(priv_hex, 16)
    priv_key = ec.derive_private_key(priv_int, ec.SECP256K1())
    serialized = json.dumps([
        0,
        event_dict["pubkey"],
        event_dict["created_at"],
        event_dict["kind"],
        event_dict["tags"],
        event_dict["content"]
    ], separators=(',', ':'), ensure_ascii=False)
    event_id = hashlib.sha256(serialized.encode()).hexdigest()
    from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature
    from cryptography.hazmat.primitives import hashes
    sig_raw = priv_key.sign(bytes.fromhex(event_id), ec.ECDSA(hashes.SHA256()))
    r, s = decode_dss_signature(sig_raw)
    sig_hex = r.to_bytes(32, 'big').hex() + s.to_bytes(32, 'big').hex()
    event_dict["id"]  = event_id
    event_dict["sig"] = sig_hex
    return event_dict

async def post_to_relay(relay_url, event):
    try:
        async with websockets.connect(relay_url, open_timeout=10) as ws:
            await ws.send(json.dumps(["EVENT", event]))
            response = await asyncio.wait_for(ws.recv(), timeout=8)
            result = json.loads(response)
            ok = result[2] if len(result) > 2 else False
            print(f"  {'✓' if ok else '✗'} {relay_url.split('/')[2]}: {result}")
    except Exception as e:
        print(f"  ✗ {relay_url.split('/')[2]}: {e}")

async def post_event(content, tags=None):
    keys = load_keys()
    event = {
        "pubkey": keys["public_key"],
        "created_at": int(time.time()),
        "kind": 1,
        "tags": tags or [],
        "content": content,
    }
    event = sign_event(event, keys["private_key"])
    tasks = [post_to_relay(r, event) for r in RELAYS]
    await asyncio.gather(*tasks)
    return event["id"]

def load_routed_packages():
    with open(LOG_FILE) as f:
        log = json.load(f)
    return [e for e in log if e.get("status") == "Routed" and e.get("summary")]

def format_post(entry):
    summary = entry["summary"]
    # Strip markdown headers for cleaner Nostr post
    lines = summary.split('\n')
    clean = '\n'.join(l for l in lines if not l.startswith('#')).strip()
    return clean[:800] + ("\n\n#BleakNarratives #Lightning #BTC #OpenSource" )

async def main():
    packages = load_routed_packages()
    print(f"Found {len(packages)} routed packages to post\n")
    posted = []
    for i, pkg in enumerate(packages):
        print(f"[{i+1}/{len(packages)}] Posting: {pkg['package_name']} → {pkg['platform']}")
        content = format_post(pkg)
        event_id = await post_event(content, tags=[
            ["t", "saas"],
            ["t", "lightning"],
            ["t", pkg["platform"].lower()]
        ])
        print(f"  Event ID: {event_id[:16]}...\n")
        posted.append({"package": pkg["package_name"], "event_id": event_id})
        await asyncio.sleep(2)  # Don't hammer relays
    
    # Save post log
    with open("/storage/emulated/0/RootBase/mrs_higgins_saas/nostr_post_log.json", "w") as f:
        json.dump(posted, f, indent=2)
    print(f"\nDone. {len(posted)} posts fired. Log saved.")

asyncio.run(main())
