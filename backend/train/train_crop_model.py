# train_crop_model.py
# Compatible with Python 3.10 + NumPy 1.26 + sklearn 1.2.2

import os
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score

import joblib

# ----------------------------------------------------
# Paths
# ----------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

DATASET_PATH = os.path.join(PROJECT_ROOT, "data", "Crop_recommendation.csv")
MODEL_DIR = os.path.join(PROJECT_ROOT, "models")

os.makedirs(MODEL_DIR, exist_ok=True)

MODEL_PATH = os.path.join(MODEL_DIR, "crop_recommendation_model.pkl")
SCALER_PATH = os.path.join(MODEL_DIR, "scaler.pkl")
ENCODER_PATH = os.path.join(MODEL_DIR, "label_encoder.pkl")

# ----------------------------------------------------
# Load dataset
# ----------------------------------------------------
print("📥 Loading dataset...")
df = pd.read_csv(DATASET_PATH)

# ----------------------------------------------------
# Encode labels
# ----------------------------------------------------
le = LabelEncoder()
df["label_encoded"] = le.fit_transform(df["label"])

X = df[["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]]
y = df["label_encoded"]

# ----------------------------------------------------
# Scale features
# ----------------------------------------------------
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# ----------------------------------------------------
# Train-test split
# ----------------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# ----------------------------------------------------
# Models
# ----------------------------------------------------
rf = RandomForestClassifier(
    n_estimators=200,
    random_state=42,
    n_jobs=-1
)

svm = SVC(
    kernel="rbf",
    probability=True,
    random_state=42
)

gb = GradientBoostingClassifier(
    n_estimators=200,
    learning_rate=0.05,
    random_state=42
)

model = VotingClassifier(
    estimators=[
        ("rf", rf),
        ("svm", svm),
        ("gb", gb)
    ],
    voting="soft"
)

# ----------------------------------------------------
# Train
# ----------------------------------------------------
print("🚜 Training Crop Recommendation Model...")
model.fit(X_train, y_train)

# ----------------------------------------------------
# Evaluate
# ----------------------------------------------------
y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"✅ Model Accuracy: {acc * 100:.2f}%")

# ----------------------------------------------------
# Save artifacts (JOBLIB ONLY)
# ----------------------------------------------------
joblib.dump(model, MODEL_PATH)
joblib.dump(scaler, SCALER_PATH)
joblib.dump(le, ENCODER_PATH)

print("💾 Saved files:")
print(" -", MODEL_PATH)
print(" -", SCALER_PATH)
print(" -", ENCODER_PATH)

print("🎉 Crop Recommendation training completed successfully!")
