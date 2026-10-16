import os, glob

pkg_dir = "./saas_packages"
out_dir = "./copy_output"
os.makedirs(out_dir, exist_ok=True)

pkgs = glob.glob(f"{pkg_dir}/*.json") + glob.glob(f"{pkg_dir}/*/*.json")
for p in pkgs:
    name = os.path.basename(p).replace(".json", "")
    out_path = os.path.join(out_dir, f"{name}_nostr.md")
    clean_name = name.replace("_", " ").title()
    
    content = f" Launching {clean_name}\n\nAutomated deployment package for Nostr nodes. High performance, zero friction.\n\n#SaaS #Nostr #BuildInPublic"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(content)

print(f"[+] Wrote {len(pkgs)} copy files to {out_dir}.")
