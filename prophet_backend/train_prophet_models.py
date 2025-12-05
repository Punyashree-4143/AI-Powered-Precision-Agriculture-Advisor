import os
import pandas as pd
from prophet import Prophet

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DATA_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "backend", "cleaned_data"))
OUTPUT_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "backend", "models"))

print("Training Prophet Models...")
print("RAW_DATA_DIR =", RAW_DATA_DIR)
print("OUTPUT_DIR =", OUTPUT_DIR)

for file in os.listdir(RAW_DATA_DIR):
    if not file.endswith(".csv"):
        continue

    try:
        path = os.path.join(RAW_DATA_DIR, file)

        # CSV format: commodity,market,ds,y
        df = pd.read_csv(path)

        commodity = df["commodity"].iloc[0]
        market = df["market"].iloc[0]

        print(f"Training {commodity} - {market}")

        model = Prophet()
        model.fit(df[["ds", "y"]])

        save_path = os.path.join(
            OUTPUT_DIR,
            f"{commodity}__{market}__prophet.pkl"
        )

        model.save(save_path)
        print(f"Saved → {save_path}")

    except Exception as e:
        print("ERROR processing:", file, e)

print("✔ DONE: All Prophet models retrained!")
