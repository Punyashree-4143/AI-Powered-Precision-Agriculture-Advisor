import requests

# -----------------------------------------------------------
# YOUR API KEY (working key you already tested)
# -----------------------------------------------------------
API_KEY = "579b464db66ec23bdd0000010bd3ce14fb4a423868045062e170054b"
BASE_URL = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"

# -----------------------------------------------------------
# District normalization for API
# -----------------------------------------------------------
DISTRICT_MAP = {
    "ramanagara": "Bengaluru Rural",   # REAL data exists here
    "kanakapura": "Bengaluru Rural",

    "bangalore urban": "Bengaluru",
    "bangalore": "Bengaluru",
    "bengaluru": "Bengaluru",
}

def normalize(value):
    if not value:
        return value
    return value.strip().lower()


# -----------------------------------------------------------
# REALTIME PRICE FUNCTION
# -----------------------------------------------------------
def get_realtime_price(commodity, ui_district, ui_market):
    """
    Returns the latest modal price as FLOAT.
    Returns None if no real-time data exists.
    """

    cd = normalize(ui_district)
    cm = normalize(commodity)
    mk = normalize(ui_market)

    # Apply mapping
    api_district = DISTRICT_MAP.get(cd, ui_district)

    # Prepare request
    params = {
        "api-key": API_KEY,
        "format": "json",
        "limit": 5,
        "filters[commodity]": commodity,
        "filters[district]": api_district,
        "filters[market_center]": ui_market
    }

    print(f"\n🔍 Checking realtime API for: {commodity} | {api_district} | {ui_market}")

    try:
        res = requests.get(BASE_URL, params=params, timeout=5)
        data = res.json()

        records = data.get("records", [])
        if not records:
            print("⚠️ No realtime data found in API")
            return None

        rec = records[0]

        # API sometimes returns `modal_price` or `modal_price (Rs./Quintal)`
        possible_keys = ["modal_price", "modal_price (Rs./Quintal)"]

        for k in possible_keys:
            if k in rec:
                try:
                    val = float(rec[k])
                    print(f"📡 Realtime modal price = {val}")
                    return val
                except:
                    pass

        print("⚠️ Valid price field not found")
        return None

    except Exception as e:
        print("⚠️ Realtime API ERROR:", e)
        return None
