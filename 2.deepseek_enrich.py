import json
import openai
import time
from pathlib import Path
from datetime import datetime

# ---------------- CONFIG ----------------

BATCH_SIZE = 1  # don't change!
MODEL = "deepseek-chat" # no websearch, for that use another LLM with the PIP.json, then recombine after validating

INPUT_FILE = "doterra_products.json"
OUTPUT_FILE = "encyclopedia.json"
PIP_FILE = "PIP.json"
API_KEY_FILE = "deepseek_api_key.txt"

# ----------------------------------------

api_key = Path(API_KEY_FILE).read_text(encoding="utf-8").strip()

client = openai.OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com"
)

SYSTEM_PROMPT = (
    "You are a strict JSON generator. "
    "Output ONLY valid JSON. No prose. No markdown."
)

TASK_PROMPT = """
You are an expert assistant specializing in essential oils, consumer health communication, and structured data extraction.

Task:
Generate a structured JSON entry for a essential oil products for use in a consumer website and oil blending tool.

Input:
- Oil name JSON

Output rules:
- Output VALID JSON ONLY
- Use 'type' and 'typeCN' fields for the category
- Follow the provided schema exactly
- Do not invent new benefit categories
- Do not use poetic or vague language
- Do not make disease treatment claims

Steps:
1. Usage
For aromatic, topical, and internal use:
- Indicate whether use is allowed
- Assign intent: primary, secondary, or supportive
- Add brief, practical notes
2. General Benefits
For EACH of the following canonical categories:
sleep, stress, mood, pain, skin, digestive, energy, respiratory, immune, focus
- Assign a score from 1 to 5
- Write a concise, factual summary (max 20 words)
3. Atomic Effects
List 2–5 atomic effects.
Each atomic effect MUST:
- Reference a biological system
- Describe a directional functional change
- Explain one or more general benefit scores
4. Primary Compounds
List the most commonly referenced major constituents if available.
5. Evidence
- Set evidence.level to low, moderate, or strong
- Set verifiedSource to ‘PIP’
6. References
Include:
- doTERRA product page URL
- doTERRA PIP URL

Constraints:
- Plain, confident language
- Consumer-safe phrasing
- No citations, no footnotes, no disclaimers
- No references to FDA or disease claims

With this schema:
‘
{
  ‘itemNo’: ‘string’,
  ‘name’: ‘string’,
  ‘size’: ‘number’,
  ‘unit’: ‘string’,

  ‘prices’: {
    ‘retail_hkd’: ‘number’,
    ‘member_hkd’: ‘number’
  },

  ‘category’: ‘Single Oil | Personal Care | doTERRA Women | Essential Oil Blends | Touch | Wellness | Supplements | Personal Care | Others’,

  ‘usage’: {
    ‘aromatic’: {
      ‘allowed’: true,
      ‘intent’: ‘primary | secondary | supportive’,
      ‘notes’: ‘string | null’
    },
    ‘topical’: {
      ‘allowed’: true,
      ‘intent’: ‘primary | secondary | supportive’,
      ‘dilutionGuidance’: ‘string | null’,
      ‘notes’: ‘string | null’
    },
    ‘internal’: {
      ‘allowed’: false,
      ‘intent’: ‘primary | secondary | supportive | null’,
      ‘notes’: ‘string | null’
    }
  },

  ‘generalBenefits’: {
    ‘sleep’: {
      ‘score’: 1,
      ‘summary’: ‘string’
    },
    ‘stress’: {
      ‘score’: 1,
      ‘summary’: ‘string’
    },
    ‘mood’: {
      ‘score’: 1,
      ‘summary’: ‘string’
    },
    ‘pain’: {
      ‘score’: 1,
      ‘summary’: ‘string’
    },
    ‘skin’: {
      ‘score’: 1,
      ‘summary’: ‘string’
    },
    ‘digestive’: {
      ‘score’: 1,
      ‘summary’: ‘string’
    },
    ‘energy’: {
      ‘score’: 1,
      ‘summary’: ‘string’
    },
    ‘respiratory’: {
      ‘score’: 1,
      ‘summary’: ‘string’
    },
    ‘immune’: {
      ‘score’: 1,
      ‘summary’: ‘string’
    },
    ‘focus’: {
      ‘score’: 1,
      ‘summary’: ‘string’
    }
  },

  ‘atomicEffects’: [
    {
      ‘mechanism’: ‘string’,
      ‘domain’: ‘nervous_system | cardiovascular | endocrine | skin_barrier | digestive | respiratory | immune’,
      ‘description’: ‘string’
    }
  ],

  ‘primaryCompounds’: [
    ‘string’
  ],

  ‘evidence’: {
    ‘level’: ‘low | moderate | strong’,
    ‘verifiedSource’: ‘PIP’
  },

  ‘references’: {
    ‘productPage’: ‘url | null’,
    ‘PIP’: ‘url | null’
  }
}
‘

Here is what an example looks like:
‘
{
  ‘itemNo’: ‘30110001’,
  ‘name’: ‘Lavender’,
  ‘size’: 15,
  ‘unit’: ‘mL’,

  ‘prices’: {
    ‘retail_hkd’: 520,
    ‘member_hkd’: 310
  },

  ‘category’: ‘Single Oil’,

  ‘usage’: {
    ‘aromatic’: {
      ‘allowed’: true,
      ‘intent’: ‘primary’,
      ‘notes’: ‘Commonly diffused for relaxation and sleep support.’
    },
    ‘topical’: {
      ‘allowed’: true,
      ‘intent’: ‘secondary’,
      ‘dilutionGuidance’: ‘Dilute for sensitive skin.’,
      ‘notes’: ‘Often applied to temples or neck.’
    },
    ‘internal’: {
      ‘allowed’: true,
      ‘intent’: ‘supportive’,
      ‘notes’: ‘Use only as directed.’
    }
  },

  ‘generalBenefits’: {
    ‘sleep’: {
      ‘score’: 5,
      ‘summary’: ‘Strong support for relaxation and restful sleep.’
    },
    ‘stress’: {
      ‘score’: 5,
      ‘summary’: ‘Helps calm the nervous system.’
    },
    ‘mood’: {
      ‘score’: 5,
      ‘summary’: ‘Supports emotional balance.’
    },
    ‘pain’: {
      ‘score’: 3,
      ‘summary’: ‘May ease mild tension.’
    },
    ‘skin’: {
      ‘score’: 4,
      ‘summary’: ‘Soothes irritated skin.’
    },
    ‘digestive’: {
      ‘score’: 2,
      ‘summary’: ‘Indirect support through relaxation.’
    },
    ‘energy’: {
      ‘score’: 1,
      ‘summary’: ‘Not stimulating.’
    },
    ‘respiratory’: {
      ‘score’: 2,
      ‘summary’: ‘Gentle inhalation support.’
    },
    ‘immune’: {
      ‘score’: 3,
      ‘summary’: ‘Supports general wellness.’
    },
    ‘focus’: {
      ‘score’: 2,
      ‘summary’: ‘Improves focus indirectly by reducing stress.’
    }
  },

  ‘atomicEffects’: [
    {
      ‘mechanism’: ‘Parasympathetic nervous system activation’,
      ‘domain’: ‘nervous_system’,
      ‘description’: ‘Associated with reduced sympathetic activity and increased relaxation.’
    },
    {
      ‘mechanism’: ‘Cortisol modulation’,
      ‘domain’: ‘endocrine’,
      ‘description’: ‘Observed reductions in stress hormone levels.’
    },
    {
      ‘mechanism’: ‘Mild antimicrobial action’,
      ‘domain’: ‘immune’,
      ‘description’: ‘Demonstrated activity against certain bacteria and fungi.’
    }
  ],

  ‘primaryCompounds’: [
    ‘Linalool’,
    ‘Linalyl acetate’
  ],

  ‘evidence’: {
    ‘level’: ‘strong’,
    ‘verifiedSource’: ‘PIP’
  },

  ‘references’: {
    ‘productPage’: ‘https://www.doterra.com/US/en/p/lavender-oil’,
    ‘PIP’: ‘https://media.doterra.com/us/en/pips/doterra-lavender-essential-oil.pdf’
  }
}
‘
"""

# ---------- LOAD INPUT ----------

def load_input():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            for v in data.values():
                if isinstance(v, list):
                    return v
        raise ValueError("Could not find input array")

# ---------- LOAD EXISTING OUTPUT ----------

def load_existing():
    if not Path(OUTPUT_FILE).exists():
        return []

    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            if isinstance(data, list):
                return data
        except Exception:
            pass

    return []

# ---------- CALL DEEPSEEK ----------

def call_deepseek(item):
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": TASK_PROMPT + "\n\nINPUT:\n" +
                json.dumps(item, ensure_ascii=False)
            }
        ],
        response_format={"type": "json_object"},  # IMPORTANT
        temperature=0,
        max_tokens=2500,
        timeout=120
    )

    content = response.choices[0].message.content

    print("\n--- RAW DEEPSEEK OUTPUT ---")
    print(content)
    print("--- END OUTPUT ---\n")

    if not content or not content.strip():
        raise ValueError("DeepSeek returned empty response")

    return json.loads(content)

# ---------- MAIN ----------

from datetime import datetime
import json
import time

OUTPUT_FILE = "encyclopedia.json"
PIP_FILE = "PIP.json"
BATCH_SIZE = 1  # assuming you defined this elsewhere


def main():
    source = load_input()
    existing = load_existing()

    existing_ids = {e.get("itemNo") for e in existing if isinstance(e, dict)}

    enriched = existing.copy()

    total = len(source)
    skipped_existing = 0
    processed = 0
    failed = 0
    new_entries = 0

    # ---------- PIP COLLECTION ----------
    pip_entries = []

    # Extract PIP from existing encyclopedia entries
    for e in existing:
        if isinstance(e, dict):
            pip_entries.append({
                "id": e.get("id") or e.get("itemNo"),
                "name": e.get("name"),
                "pip": e.get("pip")
            })

    print(f"Total source items: {total}")
    print(f"Existing encyclopedia entries: {len(existing_ids)}")
    print("-" * 50)

    for i in range(0, total, BATCH_SIZE):
        item = source[i]

        item_id = item.get("itemNo")

        if item_id in existing_ids:
            skipped_existing += 1
            continue

        print(f"→ Processing: {item.get('name')} ({item_id})")

        try:
            result = call_deepseek(item)

            if not isinstance(result, dict):
                raise ValueError("DeepSeek did not return a JSON object")

            # Add lastUpdated programmatically
            result["lastUpdated"] = datetime.utcnow().strftime("%Y-%m-%d")

            enriched.append(result)
            existing_ids.add(item_id)

            # ---------- ADD TO PIP LIST ----------
            pip_entries.append({
                "id": result.get("id") or result.get("itemNo"),
                "name": result.get("name"),
                "pip": result.get("references", {}).get("PIP")
            })

            processed += 1
            new_entries += 1

        except Exception as e:
            failed += 1
            print(f"⚠️ Failed: {item.get('name')} | {e}")

        time.sleep(0.4)  # polite delay

    # ---------- WRITE encyclopedia.json ----------
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(enriched, f, ensure_ascii=False, indent=2)

    # ---------- WRITE PIP.json ----------
    # Deduplicate by id (PIP.json must be clean)
    seen = set()
    pip_clean = []
    for p in pip_entries:
        pid = p.get("id")
        if pid and pid not in seen:
            seen.add(pid)
            pip_clean.append(p)

    with open(PIP_FILE, "w", encoding="utf-8") as f:
        json.dump(pip_clean, f, ensure_ascii=False, indent=2)

    # ---------- SUMMARY ----------

    print("\n" + "=" * 60)
    print("DEEPSEEK ENRICHMENT SUMMARY")
    print("=" * 60)
    print(f"Total source items:       {total}")
    print(f"Already existed (skip):   {skipped_existing}")
    print(f"Newly enriched:          {new_entries}")
    print(f"Failed:                  {failed}")
    print(f"Final encyclopedia size: {len(enriched)}")
    print(f"PIP entries exported:    {len(pip_clean)}")
    print(f"Output files:")
    print(f" - {OUTPUT_FILE}")
    print(f" - {PIP_FILE}")
    print("=" * 60)
    print("Done.")

if __name__ == "__main__":
    main()
