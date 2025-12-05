import pandas as pd
import os

BASE = os.path.dirname(os.path.abspath(__file__))

# CSV auto-detection
possible_paths = [
    os.path.join(BASE, "market_price", "karnataka_data.csv"),
    os.path.join(BASE, "karnataka_data.csv"),
]

CSV_PATH = None
for p in possible_paths:
    if os.path.exists(p):
        CSV_PATH = p
        break

if not CSV_PATH:
    print("❌ CSV not found")
    exit()

df = pd.read_csv(CSV_PATH, low_memory=False)

# Normalize strings
df["District_low"] = df["District"].str.lower()
df["Commodity_low"] = df["Commodity"].str.lower()

# Check for Potato in Bangalore
mask = (
    df["District_low"] == "bangalore"  # EXACT spelling from your District list
) & (
    df["Commodity_low"].str.contains("potato")
)

subset = df.loc[mask, ["District", "Market", "Commodity", "Arrival_Date", "Modal_Price"]]

print("\n🔎 TOTAL POTATO ROWS FOUND FOR BANGALORE:", len(subset))
print("\n🟦 Unique Markets:")
print(subset["Market"].unique())

print("\n🟨 Unique Commodity Names:")
print(subset["Commodity"].unique())

print("\n📅 Sample Rows (first 10):")
print(subset.head(10))
