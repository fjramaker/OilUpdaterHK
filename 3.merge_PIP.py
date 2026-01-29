import json

def merge_pip_into_encyclopedia(
    encyclopedia_path="encyclopedia.json",
    pip_path="PIP.json",
    output_path="encyclopedia_merged.json"
):
    with open(encyclopedia_path, "r", encoding="utf-8") as f:
        encyclopedia = json.load(f)

    with open(pip_path, "r", encoding="utf-8") as f:
        pip_list = json.load(f)

    # Build lookup table from PIP.json
    pip_map = {item["id"]: item["pip"] for item in pip_list}

    updated = 0
    missing = 0

    for item in encyclopedia:
        oil_id = item.get("id")
        if oil_id in pip_map:
            item["pip"] = pip_map[oil_id]
            updated += 1
        else:
            missing += 1

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(encyclopedia, f, indent=2, ensure_ascii=False)

    print("=== PIP MERGE SUMMARY ===")
    print(f"Total encyclopedia entries: {len(encyclopedia)}")
    print(f"PIP links updated: {updated}")
    print(f"No PIP entry found for: {missing}")
    print(f"Output written to: {output_path}")
