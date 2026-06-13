# scripts/daily_collector.py
import requests
import pandas as pd
import datetime
import os
import subprocess
from dotenv import load_dotenv

# ── CONFIG ──────────────────────────────────────────────────
load_dotenv()
API_KEY  = os.getenv("METAL_API_KEY")

HEADERS = {
    "x-rapidapi-key" : API_KEY,
    "x-rapidapi-host": "metal-sentinel.p.rapidapi.com"
}

CSV_PATH = r"C:\Users\Trach\OneDrive\Desktop\python journey\Project_5\data\nickel_clean.csv"

# ── FETCH LIVE PRICE ────────────────────────────────────────
def get_live_nickel():
    querystring = {"symbol":"NI","currency":"USD"}
    response=requests.get(
        "https://metal-sentinel.p.rapidapi.com/metal-quote",
        headers=HEADERS,
        params=querystring
    )

    data = response.json()["results"][0]
    
    price_usd_lb = data["mid"]
    price_usd_kg = price_usd_lb * 2.20462
    price_usd_mt = price_usd_lb * 2204.62
    price_vnd_kg = price_usd_kg * 26300


    return {
        "Date": datetime.date.today().isoformat(),

        "Price": price_usd_mt,
        "Open": data["open"] * 2204.62,
        "High": data["high"] * 2204.62,
        "Low": data["low"] * 2204.62,

        "Change %": data["changePercentage"],

        "USD_per_mt": price_usd_mt,
        "USD_per_kg": price_usd_kg,
        "VND_per_kg": price_vnd_kg
    }

# APPEND TO CSV
try:
    today_data = get_live_nickel()
    new_row = pd.DataFrame([today_data])
    
    if os.path.exists(CSV_PATH):
        history = pd.read_csv(CSV_PATH)
        if today_data["Date"] in history["Date"].values:
            print("Today's data already exists.")
            exit()
        # Calculate change % from yesterday's price
        yesterday_price = history["VND_per_kg"].iloc[-1]
        today_price = today_data["VND_per_kg"]
        change_pct = ((today_price - yesterday_price) / yesterday_price * 100)
        
        new_row["Change %"] = round(change_pct, 2)
        
        history = pd.concat([history, new_row], ignore_index=True)
    else:
        new_row["Change %"] = 0.0  # first row, no yesterday
        history = new_row
    
    history.to_csv(CSV_PATH, index=False)
    
    change_pct = new_row["Change %"].iloc[0]
    print(f"✓ Saved {today_data['Date']}")
    print(f"  Price: {today_data['VND_per_kg']:,.0f} VND/kg")
    print(f"  Change: {change_pct:+.2f}%")
    # commit to git hub
    REPO_PATH = r"C:\Users\Trach\OneDrive\Desktop\python journey\project_5"
    os.chdir(REPO_PATH)
    subprocess.run(["git", "add", "data/nickel_daily.csv"], check=True)
    subprocess.run([
        "git", "commit", "-m", 
        f"Auto-update: {today_data['Date']} — ${today_data['USD_per_kg']:.2f}/kg"
    ], check=True)
    subprocess.run(["git", "push"], check=True)
    
    print(f"✓ Pushed to GitHub")
except Exception as e:
    print(f"✗ Error: {e}")