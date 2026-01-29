import requests
import pdfplumber
import re
import json
import io
import os

# pip install pdfplumber
# source code for DoTerra_Pricing_Tool.exe

PDF_URL = "https://media.doterra.com/hk-otg/zh/brochures/hkotg-price-list.pdf"

def is_chinese_char(char):
    return u'\u4e00' <= char <= u'\u9fff'

def split_bilingual_text(text):
    """Splits text into English and Chinese parts."""
    for i, char in enumerate(text):
        if is_chinese_char(char):
            return text[:i].strip(), text[i:].strip()
    return text.strip(), ""

def parse_row(line):
    line = line.strip()
    
    # 1. Price Regex (The robust "block" version)
    price_pattern = r'((?:\s+[0-9,]+\.\d{2}){2,4})$'
    price_match = re.search(price_pattern, line)
    
    if not price_match: return None

    prices_str = price_match.group(1).strip()
    prices = re.split(r'\s+', prices_str)
    
    retail_raw = prices[0].replace(',', '')
    member_raw = prices[1].replace(',', '')
    
    # 2. Leftover Content
    leftover = line[:price_match.start()].strip()
    
    # 3. ID and Name
    id_match = re.match(r'^(\d+)\s+(.*)', leftover)
    if not id_match: return None
    
    item_id = id_match.group(1)
    content = id_match.group(2).strip()
    
    # 4. Size/Unit extraction
    size_match = re.search(r'(\d+)\s*([a-zA-Z\s/]+[\u4e00-\u9fff/]*.*)$', content)
    
    size_val, unit_str, name_str = "1", "Count", content
    if size_match:
        size_val = size_match.group(1)
        unit_str = size_match.group(2).strip()
        name_str = content[:size_match.start()].strip()

    # 5. Fix "Stray Digits" (The '395' fix)
    stray_digit_match = re.search(r'\s+(\d+)$', unit_str)
    if stray_digit_match:
        stray_digit = stray_digit_match.group(1)
        retail_raw = stray_digit + retail_raw # Prepend missing digit to price
        unit_str = unit_str[:stray_digit_match.start()].strip() # Remove from unit

    # 6. Split Name
    name_en, name_cn = split_bilingual_text(name_str)
    if not name_en: name_en = name_str

    # 7. Clean Unit
    unit_en, unit_cn = unit_str, ""
    if "/" in unit_str:
        parts = unit_str.split('/')
        unit_en, unit_cn = parts[0].strip(), parts[1].strip()
    elif len(unit_str) > 0 and is_chinese_char(unit_str[-1]):
        unit_en, unit_cn = split_bilingual_text(unit_str)

    # Clean the Chinese unit of trailing garbage
    unit_cn_match = re.match(r'^([\u4e00-\u9fff]+)', unit_cn)
    if unit_cn_match: unit_cn = unit_cn_match.group(1)

    return {
        "itemNo": item_id,
        "name": name_en,
        "nameCN": name_cn,
        "size": size_val,
        "unit": unit_en,
        "unitCN": unit_cn,
        "retail_hkd": float(retail_raw),
        "member_hkd": float(member_raw)
    }

def run_scraper():
    print("Fetching PDF...")
    response = requests.get(PDF_URL)
    products = []
    
    # State variables to track the current Category Header
    current_type_en = "Uncategorized"
    current_type_cn = ""
    
    # Words to ignore if found in a non-product line
    ignored_keywords = ["Item No", "Product", "Wholesale", "Retail", "PV", "Unit", "LRP", "Point", "Redemption", "產品編號"]

    with pdfplumber.open(io.BytesIO(response.content)) as pdf:
        print(f"Scanning {len(pdf.pages)} pages...")
        
        for page in pdf.pages:
            text = page.extract_text()
            if not text: continue
            
            lines = text.split('\n')
            for line in lines:
                line = line.strip()
                if not line: continue

                # CHECK 1: Is this a Product Line? (Starts with ID digits + contains prices)
                if re.match(r'^\d{5,}', line) and "." in line:
                    data = parse_row(line)
                    if data:
                        # Inject the current Category Header we found previously
                        data['type'] = current_type_en
                        data['typeCN'] = current_type_cn
                        
                        # Add a helper for your calculator
                        data['is_oil'] = True if "mL" in data['unit'] else False
                        
                        products.append(data)
                
                # CHECK 2: Is this a Category Header?
                # It's NOT a product, NOT a price row, and NOT a table header keyword
                elif not re.search(r'[0-9]+\.[0-9]{2}', line): # No prices
                    is_garbage = False
                    for kw in ignored_keywords:
                        if kw in line:
                            is_garbage = True
                            break
                    
                    if not is_garbage:
                        # Assume this line is a Category Header (e.g., "Single Oils 單方精油")
                        # We try to split it into EN/CN
                        head_en, head_cn = split_bilingual_text(line)
                        
                        # Basic validation: headers usually have letters
                        if len(head_en) > 2:
                            current_type_en = head_en
                            current_type_cn = head_cn
                            # print(f"--- New Category Detected: {current_type_en} ---")

    # Open old JSON and compare, then save JSON
    filename = 'doterra_products.json'
    old_products = {}
    
    # 1. Load existing data if available
    if os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                old_list = json.load(f)
                # Convert list to dict (Key: ItemNo) for fast lookup
                old_products = {p['itemNo']: p for p in old_list}
        except Exception:
            pass # File might be empty or corrupt, treat as fresh run

    # 2. Analyze Changes
    new_products_map = {p['itemNo']: p for p in products}
    
    added_items = []
    changed_prices = [] # Stores percentage changes
    removed_items = []

    # Check for Added items and Price Changes
    for pid, new_p in new_products_map.items():
        if pid not in old_products:
            added_items.append(new_p['name'])
        else:
            old_p = old_products[pid]
            # Compare Member Price (Business relevant)
            if old_p['member_hkd'] != new_p['member_hkd']:
                old_price = old_p['member_hkd']
                new_price = new_p['member_hkd']
                if old_price > 0:
                    pct = ((new_price - old_price) / old_price) * 100
                    changed_prices.append(pct)

    # Check for Removed items
    for pid, old_p in old_products.items():
        if pid not in new_products_map:
            removed_items.append(f"{old_p['name']} ({pid})")

    # 3. Save NEW data to JSON (Overwriting old file)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)

    # 4. Print Summary Report
    print("\n" + "="*50)
    print(f"  DATA REFRESH SUMMARY")
    print("="*50)
    print(f"  Total Active Products:   {len(products)}")
    print(f"  New Products Added:      {len(added_items)}")
    print(f"  Products Removed:        {len(removed_items)}")
    
    if removed_items:
        # Show first 3 removed items, then truncate
        display_rem = removed_items[:3]
        if len(removed_items) > 3: display_rem.append(f"...and {len(removed_items)-3} more")
        print(f"    -> Gone: {', '.join(display_rem)}")

    print(f"  Price Changes Detected:  {len(changed_prices)}")
    
    if changed_prices:
        avg_change = sum(changed_prices) / len(changed_prices)
        direction = "INCREASE" if avg_change > 0 else "DECREASE"
        print(f"    -> Average Change:     {avg_change:+.2f}% ({direction})")
    
    print("="*50 + "\n")
        
    print(f"Success! Scraped {len(products)} products.")
    # Show example of the "type" field working
    if len(products) > 0:
        print("\nSample Output:")
        print(json.dumps(products[0], ensure_ascii=False, indent=2))

if __name__ == "__main__":
    try:
        run_scraper()
    except Exception as e:
        print(f"\nCRITICAL ERROR: {e}")
    
    # KEEPS THE WINDOW OPEN
    input("\nProcess Complete! Press Enter to close this window...")