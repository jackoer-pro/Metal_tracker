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
HEADERS = {
    "x-rapidapi-key" : API_KEY,
    "x-rapidapi-host": "metal-sentinel.p.rapidapi.com",
}
#Load history
nickel_history = pd.read_csv(r"C:\Users\Trach\OneDrive\Desktop\python journey\Project_5\data\nickel_clean.csv", parse_dates=["Date"])
print("✓ Historical nickel data loaded")
print(f"  {len(nickel_history)} days (2006-2026)")
# fetch live nickel price
#%%
def get_live_nickel():
    querystring = {"symbol":"NI","currency":"USD"}
    response=requests.get(
        "https://metal-sentinel.p.rapidapi.com/metal-quote",
        headers=HEADERS,
        params=querystring
    )

    data=response.json()['results'][0]
    price_usd_lb=data["mid"]
    price_usd_kg = price_usd_lb * 2.20462
    price_vnd_kg = price_usd_kg * 26300

    return{
        "price_usd_lb"  : price_usd_lb,
        "price_usd_kg"  : price_usd_kg,
        "price_vnd_kg"  : price_vnd_kg,
        "change_pct"    : data["changePercentage"],
        "high_usd_lb"   : data["high"],
        "low_usd_lb"    : data["low"],
        "timestamp"     : data["originalTime"]
    }
# Run it
live=get_live_nickel()
print("\n✓ Live nickel price fetched")
print(f"  ${live['price_usd_lb']:.2f}/lb")
print(f"  {live['price_vnd_kg']:,.0f} VND/kg")
print(f"  Daily change: {live['change_pct']:+.2f}%")
print(f"  Timestamp: {live['timestamp']}")
# Alert Logic
today_price=live["price_vnd_kg"]
cutoff_7d = pd.Timestamp.today() - pd.Timedelta(days=7)

price_7d_ago = nickel_history[
    nickel_history['Date'] < cutoff_7d
]['VND_per_kg'].iloc[-1]
cutoff_30d = pd.Timestamp.today() - pd.Timedelta(days=30)

price_30d_ago = nickel_history[
    nickel_history['Date'] < cutoff_30d
]['VND_per_kg'].iloc[-1]

change_7d = ((today_price - price_7d_ago) / price_7d_ago * 100)
change_30d = ((today_price - price_30d_ago) / price_30d_ago * 100)

print(f"Price trends:")
print(f"  7-day:  {change_7d:+.1f}%")
print(f"  30-day: {change_30d:+.1f}%")

# Signal: based on TREND not daily noise
if change_7d > 5 or change_30d > 10:
    signal = "🔴 BUY NOW — uptrend confirmed. Supplier prices will likely rise in 4-8 weeks"
elif change_7d < -5 or change_30d < -10:
    signal = "🟢 WAIT — downtrend. Supplier prices will likely fall. Hold off buying"
else:
    signal = "🟡 STABLE — no clear trend. Proceed with normal ordering"

print(f"\nSignal for mom: {signal}")
# %%
import yfinance as yf
import numpy as np # for better calculation
from scipy.stats import pearsonr # correlation coefficient
# try to find the correlation between iron ore and nickel, two of the most prominent factor in steel
#%%
#load the data to investigate
iron=pd.read_csv(r"C:\Users\Trach\OneDrive\Desktop\python journey\Project_5\data\iron_daily_20y.csv", parse_dates=["Date"])
print(f"Loaded: {len(iron)} rows")
print(f"Date range: {iron['Date'].min().date()} → {iron['Date'].max().date()}")
print(f"Missing prices: {iron['Price'].isna().sum()}")
print(iron.head(5))
# clean it 
iron["Price"] = iron["Price"].replace(",", "").astype(float)
iron["Open"]  = iron["Open"].replace(",", "").astype(float)
iron["High"]  = iron["High"].replace(",", "").astype(float)
iron["Low"]   = iron["Low"].replace(",", "").astype(float)
# sort by date descending
iron=iron.sort_values("Date").reset_index()
# drop unwanted columns
iron=iron[["Date", "Price", "Open", "High", "Low", "Change %"]]
# Convert change % to float
iron["Change %"] = iron["Change %"].str.replace("%", "").astype(float)
# Convert: USD/tonne → USD/kg → VND/kg
iron["USD_per_mt"]  = iron["Price"]           # metric tonne
iron["USD_per_kg"]  = iron["USD_per_mt"] / 1000
iron["VND_per_kg"]  = iron["USD_per_kg"] * 26300
# save cleaned data
iron.to_csv(r"C:\Users\Trach\OneDrive\Desktop\python journey\Project_5\data\iron_clean.csv", index=False)
print("✓ Cleaned iron data (USD/metric tonne)")
print(f"Date range: {iron['Date'].min().date()} → {iron['Date'].max().date()}")
print(f"\nLast 5 rows (most recent):")
print(iron.tail(5)[["Date", "USD_per_mt", "USD_per_kg", "VND_per_kg"]])
# %%
nickel=pd.read_csv(r"C:\Users\Trach\OneDrive\Desktop\python journey\Project_5\data\nickel_clean.csv", parse_dates=["Date"])
nickel=nickel[["Date", "VND_per_kg"]].rename(columns={"VND_per_kg":"Nickel"})
iron_ore = pd.read_csv(r"C:\Users\Trach\OneDrive\Desktop\python journey\Project_5\data\iron_clean.csv", parse_dates=["Date"])
iron_ore=iron_ore[["Date", "VND_per_kg"]].rename(columns={"VND_per_kg":"Iron"})
# merge two data to see the correlation
data=nickel.merge(iron_ore, on="Date", how="inner")
print(f"✓ Merged data: {len(data)} trading days")
print(f"  Date range: {data['Date'].min().date()} → {data['Date'].max().date()}")
# start to calculate the correlation 
nickel_val = data["Nickel"].values
iron_val = data["Iron"].values

corr, p_value = pearsonr(nickel_val, iron_val)
print(f"\n✓ Correlation Analysis:")
print(f"  Nickel ↔ Iron Ore: {corr:+.3f}")
print(f"  P-value: {p_value:.2e}")
print(f"\nInterpretation:")
if corr > 0.7:
    print(f"  STRONG correlation — they move together closely")
    print(f"  When iron ore rises → nickel usually rises too")
elif corr > 0.4:
    print(f"  MODERATE correlation — they move somewhat together")
elif corr > 0:
    print(f"  WEAK correlation — they move loosely together")
else:
    print(f"  NEGATIVE correlation — they move opposite directions")


# %%
