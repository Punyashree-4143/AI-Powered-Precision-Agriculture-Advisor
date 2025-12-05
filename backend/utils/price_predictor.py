# backend/utils/price_predictor.py
"""
Utilities for:
- Extracting historical modal prices from CSV
- Preparing ML features
- Training XGBoost model on the fly (fallback)
"""

import pandas as pd
import numpy as np
import xgboost as xgb
import os

# OPTIONAL: attach real-time API (non-blocking)
try:
    from market_price.realtime_api import get_realtime_price
except Exception:
    def get_realtime_price(*args, **kwargs):
        return None


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "market_price", "karnataka_data.csv")
MODEL_DIR = os.path.join(BASE_DIR, "market_price", "models")

os.makedirs(MODEL_DIR, exist_ok=True)


# -----------------------------------------------------------
# LOAD CSV + (OPTIONAL) APPEND TODAY'S REALTIME PRICE
# -----------------------------------------------------------
def load_price_history(district, market, commodity, required_days=60):

    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError(f"Karnataka CSV missing at {CSV_PATH}")

    df = pd.read_csv(CSV_PATH, parse_dates=["Arrival_Date"], low_memory=False)
    df.columns = [c.strip() for c in df.columns]

    mask = (
        (df["District"].str.lower() == district.lower()) &
        (df["Market"].str.lower() == market.lower()) &
        (df["Commodity"].str.lower() == commodity.lower())
    )

    subset = df.loc[mask, ["Arrival_Date", "Modal_Price"]].dropna()
    if subset.empty:
        return pd.Series(dtype=float)

    subset = subset.sort_values("Arrival_Date")
    series = subset.set_index("Arrival_Date")["Modal_Price"]

    # ⚡ NEW: Real-Time Price Injection (non-breaking)
    try:
        rt_price = get_realtime_price(commodity, district, market)
        if rt_price is not None:
            today = pd.Timestamp.now().normalize()
            # Only insert if date not already present
            if today not in series.index:
                series.loc[today] = float(rt_price)
    except Exception:
        pass

    return series.tail(required_days)



# -----------------------------------------------------------
# FEATURE CREATION
# -----------------------------------------------------------
def make_features(series: pd.Series):
    df = pd.DataFrame(series)
    df["lag_1"]  = df["Modal_Price"].shift(1)
    df["lag_7"]  = df["Modal_Price"].shift(7)
    df["lag_14"] = df["Modal_Price"].shift(14)

    df["roll_mean_7"]  = df["Modal_Price"].shift(1).rolling(7).mean()
    df["roll_mean_14"] = df["Modal_Price"].shift(1).rolling(14).mean()

    df = df.dropna()
    X = df[["lag_1", "lag_7", "lag_14", "roll_mean_7", "roll_mean_14"]]
    y = df["Modal_Price"]

    return X, y


# -----------------------------------------------------------
# TRAIN MODEL AUTOMATICALLY IF MISSING
# -----------------------------------------------------------
def train_model_auto(district, market, commodity):
    """
    Automatically trains XGBoost when model is missing.
    Saves model to market_price/models/
    """

    series = load_price_history(district, market, commodity, required_days=120)
    if len(series) < 20:
        raise ValueError("Not enough history to train")

    X, y = make_features(series)

    model = xgb.XGBRegressor(
        n_estimators=120,
        learning_rate=0.1,
        max_depth=6,
        subsample=0.9,
        colsample_bytree=0.9,
        objective="reg:squarederror"
    )

    model.fit(X, y)

    # Save
    fname = f"{district}_{market}_{commodity}.joblib".replace(" ", "_")
    path = os.path.join(MODEL_DIR, fname)

    import joblib
    joblib.dump(model, path)

    print(f"🟢 TRAINED + SAVED: {fname}")
    return model


# -----------------------------------------------------------
# PREPARE FEATURES FOR FORECASTING (ITERATIVE)
# -----------------------------------------------------------
def prepare_predict_features(model, recent_prices: pd.Series):

    last = recent_prices.tolist()[::-1]  # latest first

    row = {
        "lag_1": last[0],
        "lag_7": last[6] if len(last) >= 7 else last[0],
        "lag_14": last[13] if len(last) >= 14 else last[0],
        "roll_mean_7": np.mean(last[:7]),
        "roll_mean_14": np.mean(last[:14])
    }

    df_row = pd.DataFrame([row])
    return df_row
