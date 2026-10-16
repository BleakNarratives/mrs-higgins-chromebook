import os
import json
import uuid
import re

REGISTRY_PATH = "/home/bleaknarratives/The-Werkz/Higgins/semantic_registry.json"
TAG_PATTERN = re.compile(r"# \[DNA_TAG: ([a-f0-9\-]+)\]")

def load_registry():
    """Loads the Whorl registry map or creates an empty one if it doesn't exist."""
    if os.path.exists(REGISTRY_PATH):
        with open(REGISTRY_PATH, 'r') as f:
            return json.load(f)
    return {}

def save_registry(registry):
    """Saves the updated map back to the JSON file."""
    with open(REGISTRY_PATH, 'w') as f:
        json.dump(registry, f, indent=4)

def tattoo_file(filepath, registry):
    """Checks a file for a DNA tag, injects one if missing, and updates the registry."""
    with open(filepath, 'r') as f:
        content = f.read()

    match = TAG_PATTERN.search(content)
    
    if match:
        file_uuid = match.group(1)
        print(f"File already tattooed: {filepath} -> {file_uuid}")
    else:
        file_uuid = str(uuid.uuid4())
        # Prepend the tag to the file
        new_content = f"# [DNA_TAG: {file_uuid}]\n" + content
        with open(filepath, 'w') as f:
            f.write(new_content)
        print(f"New tattoo applied: {filepath} -> {file_uuid}")

    # Always update the registry with the current path to ensure it is accurate
    registry[file_uuid] = filepath
    return registry

def scan_sector(directory):
    """Scans a directory recursively and tattoos all Python files."""
    registry = load_registry()
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.abspath(os.path.join(root, file))
                registry = tattoo_file(filepath, registry)
                
    save_registry(registry)
    print(f"\nSector scan complete. Registry updated at {REGISTRY_PATH}")

if __name__ == "__main__":
    # Example usage: Set this to the target sector
    TARGET_SECTOR = "/home/bleaknarratives/r11"
    
    if os.path.exists(TARGET_SECTOR):
        print(f"Initiating Floor Hatch sequence on sector: {TARGET_SECTOR}")
        scan_sector(TARGET_SECTOR)
    else:
        print(f"Directory not found: {TARGET_SECTOR}")
