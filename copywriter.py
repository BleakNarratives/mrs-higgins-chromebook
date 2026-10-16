import json, os, sys, argparse, urllib.request, urllib.error

OPENROUTER_URL   = os.getenv("OPENROUTER_URL", "https://openrouter.ai/api/v1")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "nex-agi/nex-n2.5-pro:free")
OPENROUTER_KEY   = os.getenv("OPENROUTER_API_KEY", "")
OUTPUT_DIR       = "copy_output"

PLATFORM_PROMPTS = {
    "Fiverr": (
        "You are a Fiverr gig copywriter. Write a punchy Fiverr gig listing. "
        "Include: Gig Title (max 80 chars), a 3-sentence Description, "
        "3 bullet FAQs, and a clear call to action. Casual, outcome-focused."
    ),
    "Upwork": (
        "You are an Upwork proposal writer. Write a professional Upwork job proposal. "
        "Opening hook (1 sentence), what you offer (2-3 sentences), "
        "specific deliverables list, closing CTA. Tone: competent, direct, no fluff."
    ),
    "Nostr": (
        "You are writing a Nostr zap post to promote a SaaS product. "
        "Max 280 characters. Lightning-native audience. Terse, technical, real. "
        "Include product name and lightning payment hook. No hashtag spam."
    ),
}

def openrouter_generate(prompt):
    import urllib.request, urllib.parse, json, os

    # Tiered fallbacks: (url, model, key)
    groq_key = os.getenv("GROQ_API_KEY") or os.getenv("OPENROUTER_API_KEY", "")
    openrouter_key = os.getenv("OPENROUTER_API_KEY", "")

    providers = [
        ("https://api.groq.com/openai/v1/chat/completions", "openai/gpt-oss-120b", groq_key),
        ("https://openrouter.ai/api/v1/chat/completions", "liquid/lfm-2.5-2.6b:free", openrouter_key),
    ]

    for url, model, key in providers:
        if not key or not key.strip():
            continue
        try:
            headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
            if "openrouter.ai" in url:
                headers["HTTP-Referer"] = "https://localhost"
                headers["X-Title"] = "Mrs Higgins SaaS"
            
            payload = json.dumps({"model": model, "messages": [{"role": "user", "content": prompt}]}).encode("utf-8")
            req = urllib.request.Request(url, data=payload, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as resp:
                res_json = json.loads(resp.read().decode("utf-8"))
                content = res_json["choices"][0]["message"]["content"]
                if content:
                    return content
        except Exception as e:
            print(f"  [Fallback engine] {model} failed: {e}. Trying next...")

    # Last resort zero-auth fallback
    try:
        encoded = urllib.parse.quote(prompt[:500])
        p_url = f"https://text.pollinations.ai/{encoded}"
        req = urllib.request.Request(p_url, headers={"User-Agent": "Mrs-Higgins/1.0"})
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.read().decode("utf-8", errors="replace").strip()
    except Exception as e:
        print(f"  [Pollinations] Error: {e}")
        return None


def generate_copy(package, platform):
    system = PLATFORM_PROMPTS.get(platform, PLATFORM_PROMPTS["Fiverr"])
    user_block = (
        f"Product Name: {package.get('name', 'Unnamed')}\n"
        f"Tagline: {package.get('tagline', '')}\n"
        f"Description: {package.get('description', '')}\n"
        f"Features: {', '.join(package.get('features', []))}\n"
        f"Pricing: {package.get('pricing_model', '')}\n"
        f"Estimated ROI: {package.get('estimated_roi_per_business', '')}"
    )
    prompt = f"{system}\n\n---\n{user_block}\n---\n\nWrite the copy now:"
    return openrouter_generate(prompt)

def run(packages_dir="./saas_packages", platform_filter=None, dry_run=False):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    if not os.path.exists(packages_dir):
        print(f"[ABORT] {packages_dir} not found.")
        return
    packages = []
    for fname in sorted(os.listdir(packages_dir)):
        if fname.endswith(".json"):
            with open(os.path.join(packages_dir, fname)) as f:
                packages.append(json.load(f))
    if not packages:
        print("[ABORT] No packages found.")
        return
    key_status = "keyed" if OPENROUTER_KEY else "no-key (Pollinations fallback)"
    print(f"[COPYWRITER] model={OPENROUTER_MODEL} | {key_status} | packages={len(packages)}")
    for pkg in packages:
        name = pkg.get("name", "unnamed")
        platforms = pkg.get("target_platforms", ["Fiverr", "Upwork"])
        if platform_filter:
            platforms = [p for p in platforms if p.lower() == platform_filter.lower()]
        for platform in platforms:
            slug = name.lower().replace(" ", "_")
            out_path = os.path.join(OUTPUT_DIR, f"{slug}_{platform.lower()}.md")
            print(f"  [{platform}] {name}...", end=" ", flush=True)
            if dry_run:
                print("[DRY]")
                continue
            copy = generate_copy(pkg, platform)
            if copy:
                with open(out_path, "w") as f:
                    f.write(f"# {name} — {platform}\n\n{copy}\n")
                print(f"[SAVED] → {out_path}")
            else:
                print("[FAIL]")
    print(f"\n[DONE] Copy in ./{OUTPUT_DIR}/")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--packages-dir", default="./saas_packages")
    parser.add_argument("--platform", default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    run(args.packages_dir, args.platform, args.dry_run)

if __name__ == "__main__":
    main()
