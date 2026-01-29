import json
import os

# Configuration
INPUT_FILE = "encyclopedia.json"
OUTPUT_FILE = "PIP.json"

def generate_pip_file():
    # 1. Load the encyclopedia data
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found.")
        return

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return

    # 2. Extract PIP entries
    pip_entries = []
    seen_ids = set()

    for entry in data:
        if not isinstance(entry, dict):
            continue

        # Use itemNo as primary ID, fallback to id
        item_id = entry.get("itemNo") or entry.get("id")
        
        # Extract PIP URL (handles both flat "pip" and nested "references.PIP")
        pip_url = entry.get("pip") or entry.get("references", {}).get("PIP")

        if item_id and item_id not in seen_ids:
            pip_entries.append({
                "id": item_id,
                "name": entry.get("name"),
                "pip": pip_url
            })
            seen_ids.add(item_id)

    # 3. Write the new PIP.json file
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(pip_entries, f, ensure_ascii=False, indent=2)

    print(f"Success! Generated {OUTPUT_FILE} with {len(pip_entries)} entries.")

if __name__ == "__main__":
    generate_pip_file()
