# doTERRA Oil Data Pipeline

This repository generates structured JSON data for doTERRA products, including prices, usage information, and benefit data.  
The output is used by the website:

https://oil-calculator-dowellness.web.app/

The repository is maintained on GitHub.  
The website consumes the raw JSON files directly from GitHub.

---

## Overview

The pipeline transforms raw doTERRA product data into enriched, structured knowledge in three stages:

1. Scrape basic product and price data
2. Enrich products with structured benefit and usage data using an LLM
3. Validate and correct official product information page (PIP) links

The final outputs are:

- `doterra_products.json` → raw product and price data
- `encyclopedia.json` → enriched product knowledge
- `PIP.json` → official product information page links

---

## Data Flow (High-Level)

doTERRA website
↓
1.oil_scraper.py
↓
doterra_products.json
↓
2.deepseek_enrich.py
↓
encyclopedia.json + PIP.json
↓
LLM link verification (manual step)
↓
merge_PIP.py
↓
final encyclopedia.json


---

## Step-by-Step Workflow

### 1) Install dependencies

From PowerShell, in the GitHub repo root folder:

```bash
pip install -r requirements.txt
(Exact packages may also be installed manually if needed.)

2) Scrape product data
Run:
- python 1.oil_scraper.py
Output:
- doterra_products.json

This file contains:
- product IDs
- names (EN + CN)
- sizes
- retail and member prices

3) Enrich product data with LLM
Run:
- python 2.deepseek_enrich.py
Outputs:
- encyclopedia.json → Structured usage, benefits, compounds, and evidence data.
- PIP.json → Product ID, name, and PIP links.

Notes:
The LLM prompt is defined in:
prompts_v2.txt and inside 2.deepseek_enrich.py

The API key is stored in:
deepseek_api_key.txt (ignored by GitHub)

This step generates Western-style scientific benefit descriptions.
(Traditional Chinese Medicine data may be added later.)

3b) Optional: regenerate PIP.json only
If only PIP.json is needed:
python 4.generate_PIP.py
Output:
- PIP.json

4) Verify PIP links using an LLM with web search
Use an external LLM with web search capability.

Input:
PIP.json - the “PIP prompt” from prompts_v2.txt

Goal:
check and correct invalid or outdated PIP URLs

Output:
corrected PIP.json

5) Merge corrected PIP links into encyclopedia.json
Run:
python merge_PIP.py
Result:
encyclopedia.json updated with verified PIP links
PIP.json treated as the source of truth for PIP URLs

# Files Used by the Website
The website loads raw JSON directly from GitHub.

Key files:
- doterra_products.json
- encyclopedia.json

These files power:
https://oil-calculator-dowellness.web.app/

Notes
The pipeline is designed to be repeatable and incremental.
Existing entries in encyclopedia.json are skipped unless regenerated.
PIP links are intentionally verified outside the main LLM pipeline due to lack of web search.
JSON structure is optimized for programmatic use, not narrative text.
