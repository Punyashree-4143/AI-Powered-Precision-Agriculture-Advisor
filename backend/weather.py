import requests

# Convert wind direction degrees → compass direction
def deg_to_direction(deg):
    dirs = [
        "North", "North-East", "East", "South-East",
        "South", "South-West", "West", "North-West"
    ]
    ix = int((deg + 22.5) // 45) % 8
    return dirs[ix]


def get_weather_data(location):
    try:
        if not location or location.strip() == "":
            return {"status": "failed", "error": "Location cannot be empty"}

        # ---------------------------------------------------
        # 1) GEOCODING (Open-Meteo)
        # ---------------------------------------------------
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={location}&count=1"
        geo_resp = requests.get(geo_url, timeout=10)

        try:
            geo_data = geo_resp.json()
        except:
            return {"status": "failed", "error": "Invalid geocoding response"}

        results = geo_data.get("results")
        if not results:
            return {"status": "failed", "error": "Location not found"}

        lat = results[0]["latitude"]
        lon = results[0]["longitude"]

        # ---------------------------------------------------
        # 2) WEATHER FORECAST (Daily + Hourly)
        # ---------------------------------------------------
        weather_url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}"
            "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,"
            "weathercode,windspeed_10m_max,winddirection_10m_dominant,"
            "uv_index_max,cloudcover_mean"
            "&hourly=relativehumidity_2m,dewpoint_2m,precipitation_probability"
            "&timezone=auto"
        )

        weather_resp = requests.get(weather_url, timeout=10)

        try:
            w = weather_resp.json()
        except:
            return {"status": "failed", "error": "Invalid weather response"}

        daily = w.get("daily", {})
        hourly = w.get("hourly", {})

        if "time" not in daily:
            return {"status": "failed", "error": "Missing forecast data"}

        # ---------------------------------------------------
        # HOURLY DATA
        # ---------------------------------------------------
        hour_time = hourly.get("time", [])
        humidity_hour = hourly.get("relativehumidity_2m", [])
        dewpoint_hour = hourly.get("dewpoint_2m", [])
        rain_prob_hour = hourly.get("precipitation_probability", [])

        # ---------------------------------------------------
        # 3) Compute Daily Humidity, Dew Point, Rain Chance
        # ---------------------------------------------------
        daily_humidity = []
        daily_rain_chance = []
        daily_dewpoint = []

        for d in daily["time"]:
            idxs = [i for i, t in enumerate(hour_time) if t.startswith(d)]

            if idxs:
                hum = sum(humidity_hour[i] for i in idxs) / len(idxs)
                dew = sum(dewpoint_hour[i] for i in idxs) / len(idxs)
                rain = sum(rain_prob_hour[i] for i in idxs) / len(idxs)
            else:
                hum = dew = rain = None

            # ⭐ FIXED: handle 0 safely (0 is valid!)
            daily_humidity.append(round(hum, 1) if hum is not None else None)
            daily_dewpoint.append(round(dew, 1) if dew is not None else None)
            daily_rain_chance.append(round(rain, 1) if rain is not None else None)

        # ---------------------------------------------------
        # 4) Build 7-Day Forecast List
        # ---------------------------------------------------
        forecast = []
        for i in range(len(daily["time"])):
            forecast.append({
                "date": daily["time"][i],
                "max_temp_c": daily["temperature_2m_max"][i],
                "min_temp_c": daily["temperature_2m_min"][i],

                # Enhanced weather
                "humidity": daily_humidity[i],
                "dew_point": daily_dewpoint[i],
                "rain_chance": daily_rain_chance[i],
                "rain_mm": daily["precipitation_sum"][i],
                "cloud_cover": daily.get("cloudcover_mean", [None])[i],
                "uv_index": daily.get("uv_index_max", [None])[i],

                # Wind info
                "wind_speed": daily["windspeed_10m_max"][i],
                "wind_direction_deg": daily["winddirection_10m_dominant"][i],
                "wind_direction": deg_to_direction(
                    daily["winddirection_10m_dominant"][i]
                ),

                # Weather code (icons)
                "weather_code": daily["weathercode"][i]
            })

        # ---------------------------------------------------
        # 5) Today's Weather
        # ---------------------------------------------------
        today_data = forecast[0] if len(forecast) > 0 else None

        # ---------------------------------------------------
        # 6) Final Response
        # ---------------------------------------------------
        return {
            "status": "success",
            "location": location,
            "latitude": lat,
            "longitude": lon,

            "today_weather": today_data,    # for UI top card
            "forecast_7_days": forecast     # for weekly grid
        }

    except Exception as e:
        return {"status": "failed", "error": str(e)}
