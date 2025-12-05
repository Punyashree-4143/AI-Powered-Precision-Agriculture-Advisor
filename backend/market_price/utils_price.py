import os
import joblib
import pandas as pd
from datetime import datetime, timedelta
import pytz

def load_model(district, market, commodity):
    safe_d = district.replace(" ", "_").replace("/", "_")
    safe_m = market.replace(" ", "_").replace("/", "_")
    safe_c = commodity.replace(" ", "_").replace("/", "_")

    models_path = os.path.join(os.path.dirname(__file__), "models")

    for f in os.listdir(models_path):
        if f.startswith(f"{safe_d}_{safe_m}_{safe_c}"):
            return joblib.load(os.path.join(models_path, f))
    return None


def get_today_ist():
    ist = pytz.timezone("Asia/Kolkata")
    return datetime.now(ist).date()


def create_features(ts_df, lags=[1,7,14], roll_windows=[7,14]):
    df_feat = ts_df.copy().sort_values("Arrival_Date")

    for l in lags:
        df_feat[f"lag_{l}"] = df_feat["Modal_Price"].shift(l)

    for w in roll_windows:
        df_feat[f"roll_mean_{w}"] = df_feat["Modal_Price"].shift(1).rolling(w).mean()

    return df_feat.dropna()


def forecast_7_days(model, ts_df):
    future = []
    temp = ts_df.copy()
    start_date = pd.to_datetime(get_today_ist())

    for i in range(7):
        feat = create_features(temp).iloc[-1:].drop(["Arrival_Date", "Modal_Price"], axis=1)
        price = model.predict(feat)[0]
        next_date = start_date + timedelta(days=i)

        temp = pd.concat([temp, 
                          pd.DataFrame({"Arrival_Date":[next_date], "Modal_Price":[price]})
                         ], ignore_index=True)

        future.append({
            "date": next_date.strftime('%Y-%m-%d'),
            "price_per_100kg": float(price),
            "price_per_kg": float(price)/100
        })
    return future
