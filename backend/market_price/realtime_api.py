# FAST VERSION — only ONE API call, no loops

import requests

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"

DISTRICT_MAP = {
    "ramanagara": "Bangalore",
}

def get_realtime_price(commodity, ui_district, ui_market):
    """Quick realtime lookup. If not found → return None immediately."""
    
    district = DISTRICT_MAP.get(ui_district.lower(), ui_district)

    params = {
        "api-key": API_KEY,
        "format": "json",
        "limit": 1,
        "filters[commodity]": commodity,
        "filters[district]": district,
        "filters[market]": ui_market
    }

    try:
        res = requests.get(BASE_URL, params=params, timeout=4).json()
        records = res.get("records", [])

        if records and "modal_price" in records[0]:
            return float(records[0]["modal_price"])
    except:
        pass

    return None
