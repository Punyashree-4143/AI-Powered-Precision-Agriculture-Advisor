# backend/market_price/price_routes.py

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import joblib
import os
import traceback

from utils.price_predictor import (
    load_price_history,
    prepare_predict_features,
    train_model_auto
)

# FAST realtime API (only 1 request, no loops)
try:
    from market_price.realtime_api import get_realtime_price
except:
    def get_realtime_price(*args, **kwargs):
        return None


price_bp = Blueprint("price_bp", __name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")
os.makedirs(MODEL_DIR, exist_ok=True)

# -------------------------------------------------------
# NEW DISTRICT → OLD DATASET DISTRICT
# -------------------------------------------------------
REAL_TO_MODEL_DISTRICT = {
    "Ramanagara": "Bangalore",
    "Channapatna": "Bangalore",
    "Kanakapura": "Bangalore",
    "Magadi": "Bangalore",

    "Bangalore": "Bangalore",
    "Bangalore Rural": "Bangalore",
    "Bangalore Urban": "Bangalore",
}


def get_model_district(real_district: str):
    """Convert UI district → dataset district (for historical CSV & model files)."""
    if not real_district:
        return real_district
    return REAL_TO_MODEL_DISTRICT.get(real_district, real_district)


# -------------------------------------------------------
# LOAD OR TRAIN MODEL
# -------------------------------------------------------
def load_or_train_model(real_district, market, commodity):
    model_district = get_model_district(real_district)

    fname = f"{model_district}_{market}_{commodity}".replace(" ", "_") + ".joblib"
    model_path = os.path.join(MODEL_DIR, fname)

    print(f"\n🛠 Loading ML model using: {model_district} | {market} | {commodity}")
    print(f"📄 Model file: {fname}")

    # Load if exists
    if os.path.exists(model_path):
        try:
            model = joblib.load(model_path)
            print("📌 Loaded existing model.")
            return model
        except:
            print("⚠️ Failed to load model — retraining...")

    # Train if missing
    return train_model_auto(model_district, market, commodity)


# -------------------------------------------------------
# 7-DAY FORECAST — FAST + CSV FALLBACK
# -------------------------------------------------------
@price_bp.route("/predict7", methods=["POST"])
def predict7():
    try:
        data = request.get_json(force=True)

        real_district = data.get("district")
        market = data.get("market")
        commodity = data.get("commodity")

        print("\n==============================")
        print("🌾 7-Day Market Forecast Request")
        print("==============================")
        print(f"District (UI): {real_district}")
        print(f"Market: {market}")
        print(f"Commodity: {commodity}")

        # VALIDATION
        if not real_district or not market or not commodity:
            return jsonify({"error": "district, market, commodity are required"}), 400

        # 1️⃣ Load ML model
        model = load_or_train_model(real_district, market, commodity)

        # 2️⃣ Load historical data (CSV)
        model_district = get_model_district(real_district)
        series = load_price_history(model_district, market, commodity, required_days=120)

        if len(series) < 14:
            return jsonify({"error": "Not enough historical data to forecast"}), 400

        # Ensure proper format
        series.index = pd.to_datetime(series.index)
        series = series.sort_index()

        last_dataset_price = float(series.iloc[-1])
        print(f"📘 Latest CSV price = {last_dataset_price}")

        # 3️⃣ REALTIME PRICE — FAST VERSION (1 API call)
        try:
            rt_price = get_realtime_price(commodity, real_district, market)
        except Exception as e:
            print("⚠️ Realtime API crashed:", e)
            rt_price = None

        # 4️⃣ APPLY CSV FALLBACK ALWAYS IF API FAILS
        if rt_price is None:
            print("⚠️ No realtime price → Using latest CSV price")
            rt_price = last_dataset_price
        else:
            print(f"📡 Realtime price used = {rt_price}")

        correction = rt_price - last_dataset_price
        print(f"📡 Final correction = {correction}")

        # 5️⃣ GENERATE 7-DAY FORECAST
        today = datetime.now()
        preds = []
        recent = series.copy()

        for i in range(1, 8):
            try:
                X = prepare_predict_features(model, recent)
                ml_pred = float(model.predict(X)[0])
            except:
                ml_pred = last_dataset_price

            final_pred = ml_pred + correction

            preds.append({
                "date": (today + timedelta(days=i)).strftime("%Y-%m-%d"),
                "predicted_price": round(final_pred, 2),
                "ml_price": round(ml_pred, 2),
                "realtime_price_used": round(rt_price, 2),
                "correction": round(correction, 2)
            })

            # Update history for next day's prediction
            next_date = recent.index.max() + pd.Timedelta(days=1)
            recent.loc[next_date] = final_pred
            recent = recent.tail(120)

        # RETURN RESPONSE
        return jsonify({
            "status": "success",
            "district": real_district,
            "market": market,
            "commodity": commodity,
            "realtime_price_used": round(rt_price, 2),
            "applied_correction": round(correction, 2),
            "predictions": preds
        })

    except Exception as e:
        tb = traceback.format_exc()
        print("❌ ERROR in predict7:", e)
        print(tb)
        return jsonify({"error": str(e), "trace": tb}), 500
