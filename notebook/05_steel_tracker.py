#%% 
import pandas as pd
#load the data to investigate
nickel=pd.read_csv(r"C:\Users\Trach\OneDrive\Desktop\python journey\Project_5\data\nickel_daily_20y.csv", parse_dates=["Date"])
print(f"Loaded: {len(nickel)} rows")
print(f"Date range: {nickel['Date'].min().date()} → {nickel['Date'].max().date()}")
print(f"Missing prices: {nickel['Price'].isna().sum()}")
print(nickel.head(5))
# clean it 
nickel["Price"] = nickel["Price"].str.replace(",", "").astype(float)
nickel["Open"]  = nickel["Open"].str.replace(",", "").astype(float)
nickel["High"]  = nickel["High"].str.replace(",", "").astype(float)
nickel["Low"]   = nickel["Low"].str.replace(",", "").astype(float)
# sort by date descending
nickel=nickel.sort_values("Date").reset_index()
# drop unwanted columns
nickel=nickel[["Date", "Price", "Open", "High", "Low", "Change %"]]
# Convert change % to float
nickel["Change %"] = nickel["Change %"].str.replace("%", "").astype(float)
# Convert: USD/tonne → USD/kg → VND/kg
nickel["USD_per_mt"]  = nickel["Price"]           # metric tonne
nickel["USD_per_kg"]  = nickel["USD_per_mt"] / 1000
nickel["VND_per_kg"]  = nickel["USD_per_kg"] * 26300
# save cleaned data
nickel.to_csv(r"C:\Users\Trach\OneDrive\Desktop\python journey\Project_5\data\nickel_clean.csv", index=False)
print("✓ Cleaned nickel data (USD/metric tonne)")
print(f"Date range: {nickel['Date'].min().date()} → {nickel['Date'].max().date()}")
print(f"\nLast 5 rows (most recent):")
print(nickel.tail(5)[["Date", "USD_per_mt", "USD_per_kg", "VND_per_kg"]])
# %%
import requests
import os
from dotenv import load_dotenv
import datetime
# config
load_dotenv()
API_KEY=os.getenv("METAL_API_KEY")
headers = {
    "x-rapidapi-key" : API_KEY,
    "x-rapidapi-host": "metal-sentinel.p.rapidapi.com",
}
#Load history
nickel_history = pd.read_csv(r"C:\Users\Trach\OneDrive\Desktop\python journey\Project_5\data\nickel_clean.csv", parse_dates=["Date"])
print("✓ Historical nickel data loaded")
print(f"  {len(nickel_history)} days (2006-2026)")