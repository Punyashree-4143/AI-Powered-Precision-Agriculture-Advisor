# backend/market_dropdowns.py

"""
Dropdown builder with corrected district grouping:
- Models keep old district names (example: Bangalore_Ramanagara_Potato.joblib)
- Dropdowns use corrected NEW district names (example: Ramanagara)
"""

import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR_CANDIDATES = [
    os.path.join(BASE_DIR, "market_price", "models"),
    os.path.join(BASE_DIR, "models"),
    os.path.join(BASE_DIR, "market_price_models"),
]

# pick the first existing model dir
MODEL_DIR = next((p for p in MODEL_DIR_CANDIDATES if os.path.isdir(p)), None)

if MODEL_DIR:
    print("🔍 Looking for models in:", MODEL_DIR)
else:
    print("🔍 Model directory not found in:", MODEL_DIR_CANDIDATES)


# -----------------------------------------
# FIX: Mapping markets → correct district
# -----------------------------------------
MARKET_TO_REAL_DISTRICT = {
    "Ramanagara": "Ramanagara",
    "Channapatna": "Ramanagara",
    "Kanakapura": "Ramanagara",

    "Doddaballa Pur": "Bangalore Rural",

    "Binny Mill (F&V), Bangalore": "Bangalore Urban",
    "Hoskote": "Bangalore Urban",
    "KR Puram": "Bangalore Urban",
}


def _clean_name(s: str) -> str:
    """Replace underscores used in filenames with spaces."""
    s2 = s.replace("%20", " ")
    s2 = re.sub(r"[_]+", " ", s2)
    return s2.strip()


# -----------------------------------------
# Build corrected dropdown CACHE
# -----------------------------------------
def build_cache():
    """Builds dropdown lists from joblib filenames but applies corrected district mapping."""
    
    cache = {
        "states": ["Karnataka"],
        "districts": {"Karnataka": set()},
        "markets": {},
        "commodities": [],
        "models": {}
    }

    if not MODEL_DIR:
        print("❌ No model directory found")
        return cache

    filenames = [f for f in os.listdir(MODEL_DIR) if f.endswith(".joblib")]

    for fname in filenames:
        # Parse: District_Market_Commodity.joblib
        stem = fname[:-7]  # remove .joblib
        parts = stem.split("_")

        if len(parts) < 3:
            continue

        old_district = _clean_name(parts[0])
        market = _clean_name(parts[1])
        commodity = _clean_name("_".join(parts[2:]))

        # -----------------------------------------
        # Use corrected district for dropdowns
        # -----------------------------------------
        corrected_district = MARKET_TO_REAL_DISTRICT.get(market, old_district)

        # Add to district list
        cache["districts"]["Karnataka"].add(corrected_district)

        # Add to markets under corrected district
        cache["markets"].setdefault(corrected_district, set()).add(market)

        # Add commodity to global list
        cache["commodities"].append(commodity)

        # Store filename under ORIGINAL keys (because models use old name)
        cache["models"][(old_district, market, commodity)] = fname

    # Convert sets → sorted lists
    cache["districts"]["Karnataka"] = sorted(cache["districts"]["Karnataka"])
    for d in cache["markets"]:
        cache["markets"][d] = sorted(cache["markets"][d])

    cache["commodities"] = sorted(list(set(cache["commodities"])))

    return cache


CACHE = build_cache()


def list_saved_models():
    if not MODEL_DIR:
        return []
    return sorted([f for f in os.listdir(MODEL_DIR) if f.endswith(".joblib")])
