# backend/models/env_disease_inference.py

import os
import base64
from tensorflow.keras.models import load_model
from tensorflow.keras.applications.efficientnet import preprocess_input
from PIL import Image
import numpy as np
import io
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "best_model.keras")
LABELS_PATH = os.path.join(BASE_DIR, "class_labels.json")
INFO_PATH = os.path.join(BASE_DIR, "disease_info.json")

print("🔍 Loading disease model...")
model = load_model(MODEL_PATH)

with open(LABELS_PATH, "r") as f:
    class_labels = json.load(f)

if os.path.exists(INFO_PATH):
    with open(INFO_PATH, "r") as f:
        DISEASE_INFO = json.load(f)
else:
    DISEASE_INFO = {}


def preprocess_image(image_bytes):
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img = img.resize((224, 224))
    arr = np.array(img)
    arr = preprocess_input(arr)
    arr = np.expand_dims(arr, axis=0)
    return arr


def predict_disease(image_bytes):
    x = preprocess_image(image_bytes)

    preds = model.predict(x)[0]
    idx = int(np.argmax(preds))
    label = class_labels[idx]
    confidence = float(preds[idx])

    label_key = label.replace(" ", "_")

    details = DISEASE_INFO.get(label_key, {
        "crop": "Unknown",
        "disease": label.replace("_", " "),
        "treatment": {
            "organic": [],
            "chemical": [],
            "prevention": []
        }
    })

    return {
        "predicted_class": label,
        "confidence": round(confidence * 100, 2),
        "crop": details["crop"],
        "disease": details["disease"],
        "treatment": details["treatment"]
    }
