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

# FAST realtime API (only 1 request)
try:
    from market_price.realtime_api import get_realtime_price
except:
    def get_realtime_price(*args, **kwargs):
        return None


price_bp = Blueprint("price_bp", __name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")
os.makedirs(MODEL_DIR, exist_ok=True)

# NEW DISTRICT → OLD DATASET DISTRICT
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
    if not real_district:
        return real_district
    return REAL_TO_MODEL_DISTRICT.get(real_district, real_district)


# -------------------------------------------------------
# LOAD OR TRAIN MODEL (UPDATED ERROR HANDLING)
# -------------------------------------------------------
def load_or_train_model(real_district, market, commodity):
    model_district = get_model_district(real_district)

    fname = f"{model_district}_{market}_{commodity}".replace(" ", "_") + ".joblib"
    model_path = os.path.join(MODEL_DIR, fname)

    print(f"\n🛠 Loading ML model using: {model_district} | {market} | {commodity}")
    print(f"📄 Model file: {fname}")

    # Load existing model if present
    if os.path.exists(model_path):
        try:
            model = joblib.load(model_path)
            print("📌 Loaded existing model.")
            return model
        except:
            print("⚠️ Failed to load model — retraining...")

    # Train if missing
    try:
        return train_model_auto(model_district, market, commodity)

    except ValueError:
        # CLEAN USER-FRIENDLY MESSAGE
        raise ValueError(
            f"No sufficient price history available for '{commodity}' in '{market}' ({real_district})."
        )

    except Exception as e:
        raise RuntimeError(f"Model training failed: {str(e)}")


# -------------------------------------------------------
# 7-DAY FORECAST — Improved Error Messaging
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

        # Validation
        if not real_district or not market or not commodity:
            return jsonify({
                "status": "error",
                "message": "District, market, and commodity are required."
            }), 400

        # 1️⃣ Load ML model
        try:
            model = load_or_train_model(real_district, market, commodity)

        except ValueError as e:
            # CLEAN MESSAGE (NO TRACEBACK)
            return jsonify({
                "status": "error",
                "message": str(e),
                "hint": "Try selecting another commodity or market."
            }), 400

        except RuntimeError as e:
            return jsonify({
                "status": "error",
                "message": "Model training failed.",
                "detail": str(e)
            }), 500

        # 2️⃣ Load historical data
        model_district = get_model_district(real_district)
        series = load_price_history(model_district, market, commodity, required_days=120)

        if len(series) < 14:
            return jsonify({
                "status": "error",
                "message": f"Not enough historical price data for '{commodity}' in '{market}'.",
                "hint": "Try another commodity or market."
            }), 400

        series.index = pd.to_datetime(series.index)
        series = series.sort_index()

        last_dataset_price = float(series.iloc[-1])
        print(f"📘 Latest CSV price = {last_dataset_price}")

        # 3️⃣ REALTIME PRICE
        try:
            rt_price = get_realtime_price(commodity, real_district, market)
        except:
            rt_price = None

        if rt_price is None:
            print("⚠️ No realtime price — using CSV fallback")
            rt_price = last_dataset_price

        correction = rt_price - last_dataset_price

        # 4️⃣ FORECAST 7 DAYS
        preds = []
        today = datetime.now()
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

            next_date = recent.index.max() + pd.Timedelta(days=1)
            recent.loc[next_date] = final_pred
            recent = recent.tail(120)

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
        print("❌ ERROR in predict7:", e)
        return jsonify({
            "status": "error",
            "message": "Unexpected server error occurred."
        }), 500
