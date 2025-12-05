# env_disease_inference.py
import os
import base64
from flask import Flask, request, jsonify
from flask_cors import CORS
from tensorflow.keras.models import load_model
from tensorflow.keras.applications.efficientnet import preprocess_input
from PIL import Image
import numpy as np
import io
import json

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "best_model.keras")
LABELS_PATH = os.path.join(BASE_DIR, "class_labels.json")
INFO_PATH = os.path.join(BASE_DIR, "disease_info.json")

print("🔍 Loading model...")
model = load_model(MODEL_PATH)

print("Model Input Shape:", model.input_shape)
print("Model Output Shape:", model.output_shape)

with open(LABELS_PATH, "r") as f:
    class_labels = json.load(f)

# Load disease information JSON
if os.path.exists(INFO_PATH):
    with open(INFO_PATH, "r") as f:
        DISEASE_INFO = json.load(f)
else:
    DISEASE_INFO = {}
    print("⚠️ WARNING: disease_info.json not found. Treatments will be empty.")


# ---------------------- IMAGE PREPROCESSING ----------------------
def preprocess_image(image_bytes):
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img = img.resize((224, 224))

    arr = np.array(img)
    arr = preprocess_input(arr)
    arr = np.expand_dims(arr, axis=0)
    return arr
# -----------------------------------------------------------------


@app.route("/predict", methods=["POST"])
def predict():
    try:
        # From form-data
        if "image" in request.files:
            img_bytes = request.files["image"].read()

        # From JSON base64
        else:
            data = request.get_json()
            b64 = data["image_base64"]
            if "," in b64:
                b64 = b64.split(",")[1]
            img_bytes = base64.b64decode(b64)

        x = preprocess_image(img_bytes)

        preds = model.predict(x)[0]
        print("Raw Predictions:", preds.tolist())

        idx = int(np.argmax(preds))
        label = class_labels[idx]  # example: "Potato Healthy"
        confidence = float(preds[idx])

        print(f"Predicted: {label} ({confidence * 100:.2f}%)")

        # -------- FIX: Convert to JSON key format --------
        label_key = label.replace(" ", "_")  # "Potato Healthy" → "Potato_Healthy"
        # --------------------------------------------------

        # Fetch details safely
        details = DISEASE_INFO.get(label_key, {
            "crop": "Unknown",
            "disease": label.replace("_", " "),
            "treatment": {
                "organic": [],
                "chemical": [],
                "prevention": []
            }
        })

        return jsonify({
            "predicted_class": label,
            "confidence": round(confidence * 100, 2),
            "crop": details["crop"],
            "disease": details["disease"],
            "treatment": details["treatment"]
        })

    except Exception as e:
        print("❌ Error:", str(e))
        return jsonify({"error": str(e)}), 500


@app.route("/", methods=["GET"])
def home():
    return {"status": "🌱 Disease Model API Running"}


if __name__ == "__main__":
    app.run(port=5001, debug=True)
