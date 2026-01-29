import json

def merge_pip_into_encyclopedia(
    encyclopedia_path="encyclopedia.json",
    pip_path="PIP.json",
    output_path="encyclopedia.json"
):
    with open(encyclopedia_path, "r", encoding="utf-8") as f:
        encyclopedia = json.load(f)

    with open(pip_path, "r", encoding="utf-8") as f:
        pip_list = json.load(f)

    # build lookup: id -> pip link
    pip_map = {item["id"]: item["pip"] for item in pip_list}

    updated = 0
    missing = 0

    for item in encyclopedia:
        item_no = item["itemNo"]

        if item_no in pip_map:
            item["references"]["PIP"] = pip_map[item_no]
            updated += 1
        else:
            missing += 1

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(encyclopedia, f, indent=2, ensure_ascii=False)

    print("=" * 50)
    print("PIP MERGE SUMMARY")
    print("=" * 50)
    print(f"Total encyclopedia entries: {len(encyclopedia)}")
    print(f"PIP links updated:         {updated}")
    print(f"Missing PIP entries:       {missing}")
    print("=" * 50)
    print("Done.")

if __name__ == "__main__":
    merge_pip_into_encyclopedia()
