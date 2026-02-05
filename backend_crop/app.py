from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pandas as pd
import os
import traceback

app = Flask(__name__)

# ✅ allow everything (DEV MODE)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")

# ----------------------------------------------------
# Load models
# ----------------------------------------------------
crop_model = joblib.load(os.path.join(MODEL_DIR, "crop_recommendation_model.pkl"))
crop_scaler = joblib.load(os.path.join(MODEL_DIR, "scaler.pkl"))
crop_le = joblib.load(os.path.join(MODEL_DIR, "label_encoder.pkl"))

# ----------------------------------------------------
# Health check (IMPORTANT for Render)
# ----------------------------------------------------
@app.route("/")
def health():
    return jsonify({
        "status": "ok",
        "service": "crop recommendation backend"
    })

# ----------------------------------------------------
# Crop Recommendation API
# ----------------------------------------------------
@app.route("/api/crop-recommend", methods=["POST", "OPTIONS"])
def crop_recommend():
    # ✅ CORS pre-flight
    if request.method == "OPTIONS":
        return "", 200

    try:
        data = request.get_json()

        X = pd.DataFrame([[
            float(data["N"]),
            float(data["P"]),
            float(data["K"]),
            float(data["temperature"]),
            float(data["humidity"]),
            float(data["ph"]),
            float(data["rainfall"])
        ]], columns=[
            "N", "P", "K",
            "temperature", "humidity",
            "ph", "rainfall"
        ])

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
        return jsonify({
            "error": str(e),
            "trace": traceback.format_exc()
        }), 500

# ----------------------------------------------------
# Run locally only (Render ignores this)
# ----------------------------------------------------
if __name__ == "__main__":
    app.run(debug=False)
