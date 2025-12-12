# app.py — MAIN BACKEND (Python 3.11 + Flask)
from flask import Flask, request, jsonify, current_app
from flask_cors import CORS
import numpy as np
import pandas as pd
import joblib
import cloudpickle
import os
import sys
import traceback
import logging
import requests
from datetime import datetime, timedelta

# -------------------------------
# AUTH IMPORTS (ADDED)
# -------------------------------
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from functools import wraps   # ✔ needed for token_required

print("RUNNING WITH PYTHON:", sys.executable)
print("VERSION:", sys.version)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("agri-backend")

# ----------------------------------------------------
# Configs
# ----------------------------------------------------
AUTO_TRAIN_MISSING_MODELS = True

BASE_FILE_DIR = os.path.dirname(os.path.abspath(__file__))
KARNATAKA_CSV_PATH = os.path.join(BASE_FILE_DIR, "market_price", "karnataka_data.csv")
MODEL_SAVE_DIR = os.path.join(BASE_FILE_DIR, "market_price", "models")

# Flask App
app = Flask(__name__)
CORS(app)

app.config["AUTO_TRAIN_MISSING_MODELS"] = AUTO_TRAIN_MISSING_MODELS
app.config["KARNATAKA_CSV_PATH"] = KARNATAKA_CSV_PATH
app.config["MODEL_SAVE_DIR"] = MODEL_SAVE_DIR

# ----------------------------------------------------
# AUTH DATABASE CONFIG (UPDATED)
# ----------------------------------------------------
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
JWT_SECRET = "MY_SUPER_SECRET_KEY"   # change later

# ----------------------------------------------------
# USER MODEL (UPDATED)
# ----------------------------------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    state = db.Column(db.String(120), nullable=True)
    district = db.Column(db.String(120), nullable=True)
    farmSize = db.Column(db.String(20), nullable=True)
    password = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

# ----------------------------------------------------
# Model directories
# ----------------------------------------------------
BASE_DIR = BASE_FILE_DIR
MODEL_DIR = os.path.join(BASE_DIR, "models")

# ----------------------------------------------------
# Helper imports
# ----------------------------------------------------
try:
    from weather import get_weather_data
except Exception:
    def get_weather_data(location):
        raise RuntimeError("weather.get_weather_data unavailable")

try:
    from market_dropdowns import CACHE
except Exception:
    CACHE = {}

# ----------------------------------------------------
# Crop Recommendation Model Load
# ----------------------------------------------------
crop_model = crop_scaler = crop_le = None
try:
    crop_model_path = os.path.join(MODEL_DIR, "crop_recommendation_model_v3.pkl")
    scaler_path = os.path.join(MODEL_DIR, "scaler.pkl")
    label_encoder_path = os.path.join(MODEL_DIR, "label_encoder.pkl")

    log.info("🔍 Loading Crop Recommendation Model...")
    if os.path.exists(crop_model_path):
        with open(crop_model_path, "rb") as f:
            crop_model = cloudpickle.load(f)

    if os.path.exists(scaler_path):
        crop_scaler = joblib.load(scaler_path)

    if os.path.exists(label_encoder_path):
        crop_le = joblib.load(label_encoder_path)

    if crop_model and crop_scaler and crop_le:
        log.info("✅ Crop Recommendation Loaded!")
    else:
        log.warning("Crop model missing components.")
except Exception:
    log.exception("❌ Crop Model Error")
    crop_model = crop_scaler = crop_le = None

# ----------------------------------------------------
# Yield Model Wrapper (NO CHANGE)
# ----------------------------------------------------
HECTARE_TO_ACRE = 2.47105
ACRE_TO_HECTARE = 0.404686
YIELD_WRAPPER_PATH = os.path.join(MODEL_DIR, "yield_ensemble_wrapper.joblib")

class EnsembleWrapper:
    def __init__(self, xgb_path=None, cat_path=None, meta_path=None):
        self.xgb_path = xgb_path
        self.cat_path = cat_path
        self.meta_path = meta_path

    def predict(self, df_input):
        preds = []

        # XGB
        if self.xgb_path and os.path.exists(self.xgb_path):
            xgb = joblib.load(self.xgb_path)
            p_xgb = xgb.predict(df_input)
        else:
            p_xgb = 0 * np.ones(len(df_input))

        # CatBoost
        p_cat = 0 * np.ones(len(df_input))
        if self.cat_path and os.path.exists(self.cat_path):
            try:
                from catboost import CatBoostRegressor
                cb = CatBoostRegressor()
                cb.load_model(self.cat_path)
                p_cat = cb.predict(df_input)
            except Exception:
                try:
                    cb = joblib.load(self.cat_path)
                    p_cat = cb.predict(df_input)
                except Exception:
                    log.exception("CatBoost load failed")

        # meta weights
        w_xgb, w_cat = 0.5, 0.5
        if self.meta_path and os.path.exists(self.meta_path):
            try:
                meta = joblib.load(self.meta_path)
                if isinstance(meta, dict):
                    w_xgb = meta.get("w_xgb", w_xgb)
                    w_cat = meta.get("w_cat", w_cat)
            except Exception:
                log.exception("Meta weights load failed")

        return w_xgb * np.array(p_xgb) + w_cat * np.array(p_cat)

def load_yield_model():
    if not hasattr(current_app, "yield_model"):
        if not os.path.exists(YIELD_WRAPPER_PATH):
            raise FileNotFoundError("Yield wrapper missing")

        log.info("🔍 Loading Yield Ensemble Model...")
        loaded = joblib.load(YIELD_WRAPPER_PATH)

        if hasattr(loaded, "predict"):
            current_app.yield_model = loaded
        elif isinstance(loaded, dict):
            current_app.yield_model = EnsembleWrapper(
                xgb_path=loaded.get("xgb"),
                cat_path=loaded.get("cat"),
                meta_path=loaded.get("meta")
            )
        else:
            class SW:
                def __init__(self, m): self.m = m
                def predict(self, X): return self.m.predict(X)
            current_app.yield_model = SW(loaded)

    return current_app.yield_model

# ----------------------------------------------------
# HOME
# ----------------------------------------------------
@app.route("/")
def home():
    return jsonify({
        "message": "🌾 AI Agriculture Advisor Backend Running",
        "modules": [
            "Crop Recommendation",
            "Yield Prediction",
            "Weather Forecast",
            "Market Price Forecast",
            "Irrigation Suggestion"
        ]
    })

# ----------------------------------------------------
# AUTH ROUTES (REGISTER + LOGIN + PROFILE + PASSWORD CHANGE)
# ----------------------------------------------------

@app.route("/api/auth/register", methods=["POST"])
def register():
    data = request.json
    name = data.get("name")
    email = data.get("email")
    phone = data.get("phone")
    state = data.get("state")
    district = data.get("district")
    farmSize = data.get("farmSize")
    password = data.get("password")

    if User.query.filter_by(email=email).first():
        return jsonify({"msg": "Email already exists"}), 400

    user = User(
        name=name,
        email=email,
        phone=phone,
        state=state,
        district=district,
        farmSize=farmSize
    )
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    return jsonify({"msg": "Registration successful"})


@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"msg": "Invalid email or password"}), 400

    token = jwt.encode(
        {"id": user.id, "email": user.email},
        JWT_SECRET,
        algorithm="HS256"
    )

    return jsonify({"token": token})


# TOKEN VERIFICATION
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            try:
                token = request.headers["Authorization"].split(" ")[1]
            except:
                return jsonify({"msg": "Invalid token format"}), 401

        if not token:
            return jsonify({"msg": "Token missing"}), 401

        try:
            data = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            user = User.query.get(data["id"])
            if not user:
                return jsonify({"msg": "User not found"}), 404
        except Exception as e:
            return jsonify({"msg": "Invalid token", "error": str(e)}), 401

        return f(user, *args, **kwargs)

    return decorated


@app.route("/api/auth/me", methods=["GET"])
@token_required
def get_profile(user):
    return jsonify({
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "phone": user.phone,
        "state": user.state,
        "district": user.district,
        "farmSize": user.farmSize
    })


@app.route("/api/auth/update-profile", methods=["PUT"])
@token_required
def update_profile(user):
    data = request.json

    user.name = data.get("name", user.name)
    user.phone = data.get("phone", user.phone)
    user.state = data.get("state", user.state)
    user.district = data.get("district", user.district)
    user.farmSize = data.get("farmSize", user.farmSize)

    db.session.commit()

    return jsonify({"msg": "Profile updated successfully"})


@app.route("/api/auth/change-password", methods=["PUT"])
@token_required
def change_password(user):
    data = request.json
    old_password = data.get("oldPassword")
    new_password = data.get("newPassword")

    if not user.check_password(old_password):
        return jsonify({"msg": "Old password incorrect"}), 400

    user.set_password(new_password)
    db.session.commit()

    return jsonify({"msg": "Password changed successfully"})

# ----------------------------------------------------
# REMAINING MODULES (UNCHANGED)
# ----------------------------------------------------
# ❗ Everything below remains exactly same as your original file  
# (Weather, Crop Recommendation, Market, Irrigation, Yield, Training, etc.)

# ----------------------------------------------------
# DROPDOWN APIs
# ----------------------------------------------------
@app.route("/api/get-states")
def get_states():
    return jsonify({"states": CACHE.get("states", [])})

@app.route("/api/get-districts")
def get_districts():
    return jsonify({"districts": CACHE.get("districts", {})})

@app.route("/api/get-markets")
def get_markets():
    district = request.args.get("district")
    return jsonify({"markets": CACHE.get("markets", {}).get(district, [])})

@app.route("/api/get-commodities")
def get_commodities():
    district = request.args.get("district")
    market = request.args.get("market")
    models_map = CACHE.get("models", {})

    if district and market:
        matches = [k[2] for k in models_map.keys() if k[0] == district and k[1] == market]
        if matches:
            return jsonify({"commodities": sorted(list(set(matches)))})

    return jsonify({"commodities": CACHE.get("commodities", [])})


# ----------------------------------------------------
# WEATHER
# ----------------------------------------------------
@app.route("/api/weather", methods=["POST"])
def weather():
    try:
        location = request.json.get("location")
        return jsonify(get_weather_data(location))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ----------------------------------------------------
# CROP RECOMMENDATION
# ----------------------------------------------------
@app.route("/api/crop-recommend", methods=["POST"])
def crop_recommend():
    try:
        data = request.get_json()

        if crop_scaler is None or crop_model is None or crop_le is None:
            return jsonify({"error": "Crop recommendation model not available"}), 500

        X = pd.DataFrame([[ 
            float(data["N"]), float(data["P"]), float(data["K"]),
            float(data["temperature"]), float(data["humidity"]),
            float(data["ph"]), float(data["rainfall"])
        ]], columns=["N", "P", "K", "temperature", "humidity", "ph", "rainfall"])

        X_scaled = crop_scaler.transform(X)
        probs = crop_model.predict_proba(X_scaled)[0]

        top3 = probs.argsort()[-3:][::-1]
        crops = crop_le.inverse_transform(top3)
        scores = [round(probs[i] * 100, 2) for i in top3]

        return jsonify({
            "recommendations": [
                {"crop": c, "confidence": s}
                for c, s in zip(crops, scores)
            ]
        })

    except Exception as e:
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500


# ----------------------------------------------------
# YIELD PREDICTION
# ----------------------------------------------------
@app.route("/api/yield-predict", methods=["POST", "OPTIONS"])
def yield_predict():

    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200

    try:
        data = request.get_json(force=True)

        required = [
            "District", "Crop", "Soil_Type", "Year",
            "Area_acre", "Annual_Rainfall_mm", "Avg_Temp_C",
            "Irrigation_Index", "Fertilizer_kg_per_ha",
            "Pesticide_kg_per_ha", "Production_tonnes"
        ]

        missing = [k for k in required if k not in data]
        if missing:
            return jsonify({"status": "error", "message": f"Missing: {missing}"}), 400

        area_acre = float(data["Area_acre"])
        area_ha = area_acre * ACRE_TO_HECTARE

        df = pd.DataFrame([{
            "District": data["District"],
            "Crop": data["Crop"],
            "Soil_Type": data["Soil_Type"],
            "Year": int(data["Year"]),
            "Area_ha": area_ha,
            "Production_tonnes": float(data["Production_tonnes"]),
            "Annual_Rainfall_mm": float(data["Annual_Rainfall_mm"]),
            "Avg_Temp_C": float(data["Avg_Temp_C"]),
            "Irrigation_Index": int(data["Irrigation_Index"]),
            "Fertilizer_kg_per_ha": float(data["Fertilizer_kg_per_ha"]),
            "Pesticide_kg_per_ha": float(data["Pesticide_kg_per_ha"])
        }])

        wrapper = load_yield_model()
        pred_t_ha = float(wrapper.predict(df)[0])

        pred_t_acre = pred_t_ha / HECTARE_TO_ACRE
        total_output = pred_t_acre * area_acre

        return jsonify({
            "status": "success",
            "Crop": data["Crop"],
            "District": data["District"],
            "area_acre": area_acre,
            "yield_ton_per_hectare": round(pred_t_ha, 4),
            "yield_ton_per_acre": round(pred_t_acre, 4),
            "total_yield_tonnes": round(total_output, 4)
        })
    except Exception as e:
        log.exception("Yield Prediction Failed")
        return jsonify({"status": "error", "message": str(e)}), 500


# ----------------------------------------------------
# IRRIGATION MODULE (UNCHANGED)
# ----------------------------------------------------
IRRIGATION_MODEL_FILENAME = "xgb_ka_global.joblib"
IRRIGATION_MODEL_PATH = os.path.join(MODEL_DIR, IRRIGATION_MODEL_FILENAME)

SOIL_MOISTURE_CSV = os.path.join(MODEL_DIR, "soil_moisture_full.csv")

SOIL_MOISTURE_DEFAULTS = {
    "Sandy": 15.0,
    "Loamy": 25.0,
    "Clay": 30.0
}

LAGS = [1, 3, 7, 14]
ROLL_WINDOWS = [3, 7, 14]

DISTRICT_COORDS = {
    "Maharashtra": {
        "Pune": {"lat": 18.5204, "lon": 73.8567},
        "Nagpur": {"lat": 21.1458, "lon": 79.0882},
    },
    "Karnataka": {
        "Bagalkote": {"lat": 16.1727, "lon": 75.6557},
        "Ballari": {"lat": 15.1394, "lon": 76.9214},
        "Belagavi": {"lat": 15.8497, "lon": 74.4977},
        "Bangalore": {"lat": 12.9716, "lon": 77.5946},
        "Bangalore Urban": {"lat": 12.9716, "lon": 77.5946},
        "Bangalore Rural": {"lat": 13.1900, "lon": 77.7040},
        "Chikkaballapur": {"lat": 13.4355, "lon": 77.7315},
        "Chitradurga": {"lat": 14.2300, "lon": 76.4000},
        "Dakshina Kannada": {"lat": 12.9141, "lon": 74.8560},
        "Davanagere": {"lat": 14.4640, "lon": 75.9218},
        "Dharwad": {"lat": 15.4589, "lon": 75.0078},
        "Gadag": {"lat": 15.4298, "lon": 75.6290},
        "Kalaburagi": {"lat": 17.3297, "lon": 76.8343},
        "Hassan": {"lat": 13.0072, "lon": 76.0996},
        "Haveri": {"lat": 14.7951, "lon": 75.3995},
        "Kolar": {"lat": 13.1367, "lon": 78.1292},
        "Kodagu": {"lat": 12.3375, "lon": 75.8069},
        "Koppal": {"lat": 15.3482, "lon": 76.1542},
        "Mandya": {"lat": 12.5223, "lon": 76.8970},
        "Mysore": {"lat": 12.2958, "lon": 76.6394},
        "Raichur": {"lat": 16.2055, "lon": 77.3554},
        "Shivamogga": {"lat": 13.9299, "lon": 75.5681},
        "Tumakuru": {"lat": 13.3409, "lon": 77.1000},
        "Udupi": {"lat": 13.3409, "lon": 74.7421},
        "Uttara Kannada": {"lat": 14.8000, "lon": 74.1300},
        "Vijayapura": {"lat": 16.8302, "lon": 75.7060},
        "Yadgir": {"lat": 16.7700, "lon": 77.1376},
    }
}

irrigation_model = None
try:
    if os.path.exists(IRRIGATION_MODEL_PATH):
        irrigation_model = joblib.load(IRRIGATION_MODEL_PATH)
        log.info(f"✅ Irrigation model loaded: {IRRIGATION_MODEL_PATH}")
    else:
        log.warning("⚠️ Irrigation model not found")
except Exception:
    log.exception("Irrigation model load failed")
    irrigation_model = None

# ----------------------------------------------------
# Soil Moisture History Loader (UNCHANGED)
# ----------------------------------------------------
def load_district_history(district_name):
    if not os.path.exists(SOIL_MOISTURE_CSV):
        log.warning("Soil moisture CSV not found: %s", SOIL_MOISTURE_CSV)
        return pd.DataFrame(columns=["Date", "State", "District", "Avg_smlvl_at15cm"])

    try:
        df = pd.read_csv(SOIL_MOISTURE_CSV)
        df.columns = [c.strip() for c in df.columns]

        if not {"Date", "Avg_smlvl_at15cm", "District"}.issubset(df.columns):
            return pd.DataFrame(columns=["Date", "State", "District", "Avg_smlvl_at15cm"])

        df["Date"] = pd.to_datetime(df["Date"])
        df = df[df["District"].str.lower() == district_name.lower()].copy()
        df = df.sort_values("Date").drop_duplicates(subset=["Date"]).reset_index(drop=True)
        return df
    except Exception:
        log.exception("Error reading soil moisture file")
        return pd.DataFrame(columns=["Date", "State", "District", "Avg_smlvl_at15cm"])


# ----------------------------------------------------
# Create Features for Prediction (UNCHANGED)
# ----------------------------------------------------
def create_features_for_prediction(df):
    df = df.copy()
    if df.empty:
        return df

    df["Date"] = pd.to_datetime(df["Date"])
    df["day"] = df["Date"].dt.day
    df["month"] = df["Date"].dt.month
    df["year"] = df["Date"].dt.year

    df["month_sin"] = np.sin(2 * np.pi * df["month"] / 12)
    df["month_cos"] = np.cos(2 * np.pi * df["month"] / 12)
    df["day_sin"] = np.sin(2 * np.pi * df["day"] / 31)
    df["day_cos"] = np.cos(2 * np.pi * df["day"] / 31)

    for l in LAGS:
        df[f"lag_{l}"] = df["Avg_smlvl_at15cm"].shift(l)

    for w in ROLL_WINDOWS:
        df[f"roll_{w}"] = df["Avg_smlvl_at15cm"].shift(1).rolling(w).mean()

    if "District" in df.columns:
        df["district_code"] = df["District"].astype("category").cat.codes
    else:
        df["district_code"] = 0

    return df


# ----------------------------------------------------
# Iterative Soil Moisture Forecast (UNCHANGED)
# ----------------------------------------------------
def iterative_forecast_soil_moisture(model, history_df, days=7, daily_weather=None, soil_type="Loamy"):

    SOIL_SENS = {"Sandy": 0.7, "Loamy": 0.5, "Clay": 0.3}
    
    sens = SOIL_SENS.get(soil_type, 0.5)

    if history_df is None or history_df.empty:
        today = pd.to_datetime("today").normalize()
        return [{
            "Date": (today + pd.Timedelta(days=i)).strftime("%Y-%m-%d"),
            "Predicted_Moisture": SOIL_MOISTURE_DEFAULTS.get(soil_type, 25.0)
        } for i in range(days)]

    df_local = history_df.copy().reset_index(drop=True)
    df_local = df_local.sort_values("Date").reset_index(drop=True)
    out = []

    rain_list = list(daily_weather.get("rain", [])) if daily_weather else []
    et0_list = list(daily_weather.get("et0", [])) if daily_weather else []

    today = pd.to_datetime("today").normalize()

    for i in range(days):
        feat = create_features_for_prediction(df_local).iloc[-1:].copy()

        if feat.empty:
            last_val = float(df_local["Avg_smlvl_at15cm"].iloc[-1])
            next_date = today + pd.Timedelta(days=i+1)
            df_local.loc[len(df_local)] = {
                "Date": next_date,
                "State": "Karnataka",
                "District": df_local["District"].iloc[-1],
                "Avg_smlvl_at15cm": last_val
            }
            out.append({"Date": next_date.strftime("%Y-%m-%d"), "Predicted_Moisture": last_val})
            continue

        Xcols = [c for c in feat.columns if c not in ["Date", "State", "District", "Avg_smlvl_at15cm"]]
        Xnew = feat[Xcols].fillna(0)

        try:
            ml_pred = float(model.predict(Xnew)[0])
        except Exception:
            ml_pred = float(df_local["Avg_smlvl_at15cm"].iloc[-1])

        rain_mm = float(rain_list[i]) if i < len(rain_list) else 0.0
        et0_mm = float(et0_list[i]) if i < len(et0_list) else 0.0

        hybrid_pred = ml_pred + sens * (rain_mm - et0_mm)
        hybrid_pred = max(0.0, min(100.0, hybrid_pred))

        next_date = (today + pd.Timedelta(days=i+1)).normalize()

        df_local.loc[len(df_local)] = {
            "Date": next_date,
            "State": "Karnataka",
            "District": df_local["District"].iloc[-1],
            "Avg_smlvl_at15cm": hybrid_pred
        }

        out.append({"Date": next_date.strftime("%Y-%m-%d"), "Predicted_Moisture": hybrid_pred})

    return out


# ----------------------------------------------------
# Calculate Irrigation Plan (UNCHANGED)
# ----------------------------------------------------
def calculate_irrigation_plan_with_model(lat, lon, crop_type, soil_type, district_name, model, forecast_days=7):

    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
            "&daily=precipitation_sum,et0_fao_evapotranspiration,precipitation_probability_max,"
            "windspeed_10m_max,uv_index_max,cloudcover_mean"
            "&timezone=auto"
        )
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        daily = resp.json().get("daily", {})

        precipitation = daily.get("precipitation_sum", [])
        et0 = daily.get("et0_fao_evapotranspiration", [])
        rain_chance = daily.get("precipitation_probability_max", [])
        wind = daily.get("windspeed_10m_max", [])
        uv = daily.get("uv_index_max", [])
        cloudcover = daily.get("cloudcover_mean", [])

    except Exception as e:
        return {"error": f"Weather API failed: {e}"}

    hist = load_district_history(district_name)

    daily_weather = {
        "rain": precipitation[:forecast_days],
        "et0": et0[:forecast_days],
        "rain_chance": rain_chance[:forecast_days],
        "wind": wind[:forecast_days],
        "uv": uv[:forecast_days],
        "cloudcover": cloudcover[:forecast_days]
    }

    preds = iterative_forecast_soil_moisture(
        model, hist, days=forecast_days, daily_weather=daily_weather, soil_type=soil_type
    )

    results = []
    for i in range(forecast_days):
        date = preds[i]["Date"]
        sm = float(preds[i]["Predicted_Moisture"])
        rain_mm = float(daily_weather["rain"][i]) if i < len(daily_weather["rain"]) else 0.0
        et0_mm = float(daily_weather["et0"][i]) if i < len(daily_weather["et0"]) else 0.0

        deficit = max(0.0, et0_mm - rain_mm)
        needs_irrigation = (sm < 20.0) or (
            deficit > 2.0
        )
        water_mm = deficit if needs_irrigation else 0.0

        results.append({
            "date": date,
            "crop": crop_type,
            "predicted_soil_moisture_percent": round(sm, 2),
            "rain_mm": round(rain_mm, 2),
            "et0_mm": round(et0_mm, 2),
            "moisture_deficit_mm": round(deficit, 2),
            "needs_irrigation": needs_irrigation,
            "water_mm": round(water_mm, 2),
            "water_l_per_hectare": round(water_mm * 10000, 2)
        })

    return results


# ----------------------------------------------------
# /api/irrigation (UNCHANGED)
# ----------------------------------------------------
@app.route("/api/irrigation", methods=["POST"])
def irrigation():
    try:
        data = request.get_json(force=True)

        crop = data.get("crop")
        state = data.get("state")
        district = data.get("district")
        soil_type = data.get("soil_type", "Loamy")

        if not crop or not state or not district:
            return jsonify({"error": "Required: crop, state, district"}), 400

        coords = DISTRICT_COORDS.get(state, {}).get(district)
        if not coords:
            for k, v in DISTRICT_COORDS.get(state, {}).items():
                if k.lower() == district.lower():
                    coords = v
                    break

        if not coords:
            return jsonify({"error": "Invalid state/district"}), 400

        lat, lon = coords["lat"], coords["lon"]

        if irrigation_model:
            plan = calculate_irrigation_plan_with_model(
                lat, lon, crop, soil_type, district, irrigation_model, forecast_days=7
            )
        else:
            return jsonify({"error": "Irrigation model not loaded"}), 500

        return jsonify(plan)

    except Exception as e:
        log.exception("Irrigation error")
        return jsonify({"error": str(e)}), 500


# ----------------------------------------------------
# TRAIN ENDPOINT (UNCHANGED)
# ----------------------------------------------------
@app.route("/api/market/train", methods=["POST"])
def train_model_endpoint():
    try:
        payload = request.get_json(force=True)
        district = payload.get("district")
        market = payload.get("market")
        commodity = payload.get("commodity")

        if not district or not market or not commodity:
            return jsonify({"error": "district, market, commodity required"}), 400

        from market_price.utils.price_predictor import train_model_for

        os.makedirs(MODEL_SAVE_DIR, exist_ok=True)

        result = train_model_for(
            district=district,
            market=market,
            commodity=commodity,
            karnataka_csv_path=KARNATAKA_CSV_PATH,
            model_dir=MODEL_SAVE_DIR
        )

        return jsonify({"status": "ok", "result": result})

    except Exception as e:
        log.exception("Training error")
        return jsonify({"error": str(e)}), 500


# ----------------------------------------------------
# MARKET PRICE FORECAST ROUTES (UNCHANGED)
# ----------------------------------------------------
try:
    from market_price.price_routes import price_bp
    app.register_blueprint(price_bp, url_prefix="/api/market")
    log.info("✅ Market price blueprint registered")
except Exception:
    log.exception("Failed to load market price blueprint")

# ----------------------------------------------------
# INIT DATABASE (ADDED)
# ----------------------------------------------------
with app.app_context():
    db.create_all()

# ----------------------------------------------------
# RUN SERVER
# ----------------------------------------------------
if __name__ == "__main__":
    app.run(port=5000, debug=False)
