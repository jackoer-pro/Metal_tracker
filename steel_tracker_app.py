# steel_tracker_app.py
import streamlit as st
import pandas as pd
import requests
import os
from dotenv import load_dotenv
import plotly.express as px
from scipy.stats import pearsonr
import datetime

# set the config
st.set_page_config(
    page_title="Steel Commodity Tracker",
    page_icon="⚙️",
    layout="wide"
)

load_dotenv()
API_KEY=os.getenv("METAL_API_KEY")
HEADERS = {
    "x-rapidapi-key" : API_KEY,
    "x-rapidapi-host": "metal-sentinel.p.rapidapi.com",
}

# LOAD DATA 
@st.cache_data
def load_historical_data():
    nickel = pd.read_csv("data/nickel_clean.csv", parse_dates=["Date"])
    nickel=nickel[["Date", "VND_per_kg"]].rename(columns={"VND_per_kg":"Nickel"})
    iron_ore = pd.read_csv("data/iron_clean.csv", parse_dates=["Date"])
    iron_ore=iron_ore[["Date", "VND_per_kg"]].rename(columns={"VND_per_kg":"Iron"})
    return nickel, iron_ore

nickel_hist, iron_ore_hist = load_historical_data()

# GET LIVE PRICE
@st.cache_data(ttl=60)  # refresh every hour
def get_live_nickel():
    querystring = {"symbol":"NI","currency":"USD"}
    response=requests.get(
        "https://metal-sentinel.p.rapidapi.com/metal-quote",
        headers=HEADERS,
        params=querystring
    )
    data = response.json()['results'][0]
    
    price_usd_lb = data["mid"]
    price_usd_kg = price_usd_lb * 2.20462
    price_vnd_kg = price_usd_kg * 26300
    
    # Calculate change % from our CSV, not API
    history = pd.read_csv("data/nickel_clean.csv")
    last_price = history["VND_per_kg"].iloc[-1]
    change_pct = ((price_vnd_kg - last_price) / last_price * 100)
    
    return {
        "price_usd_lb" : price_usd_lb,
        "price_usd_kg" : price_usd_kg,
        "price_vnd_kg" : price_vnd_kg,
        "change_pct"   : change_pct,
        "timestamp"    : datetime.date.today().isoformat()  # use today's date, not API
    }

# ── PAGE NAVIGATION ────────────────────────────────────────
st.title("⚙️ Steel Commodity Tracker")
st.caption("Real-time nickel & iron ore prices for inventory decisions")

page = st.sidebar.radio(
    "Navigate",
    ["Live Prices", "Trends", "Correlation"]
)

# ── PAGE 1: LIVE PRICES ────────────────────────────────────
if page == "Live Prices":
    st.subheader("Live Nickel Price")
    
    try:
        live = get_live_nickel()
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Price", f"{live['price_vnd_kg']:,.0f} VND/kg", f"{live['change_pct']:+.2f}%")
        col2.metric("USD per kg", f"${live['price_usd_kg']:.2f}")
        col3.metric("Last updated", live['timestamp'][:10])
        
        # Alert logic
        price_7d_ago = nickel_hist[nickel_hist['Date'] < pd.Timestamp.now() - pd.Timedelta(days=7)]['Nickel'].iloc[-1]
        change_7d = ((live['price_vnd_kg'] - price_7d_ago) / price_7d_ago * 100)
        
        if change_7d > 5:
            st.error(f"🔴 BUY NOW — Nickel up {change_7d:.1f}% (7 days). Supplier prices will rise in 4-8 weeks.")
        elif change_7d < -5:
            st.success(f"🟢 WAIT — Nickel down {change_7d:.1f}% (7 days). Supplier prices will likely fall.")
        else:
            st.info(f"🟡 STABLE — Nickel change {change_7d:+.1f}% (7 days). Proceed normally.")
            
    except Exception as e:
        st.error(f"Error fetching live price: {e}")

# ── PAGE 2: TRENDS ─────────────────────────────────────────
elif page == "Trends":
    st.subheader("Historical Nickel Price (20 years)")
    
    fig = px.line(nickel_hist, x="Date", y="Nickel",
                  title="Nickel Price Trend",
                  labels={"Nickel": "Price (VND/kg)"})
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)
    
    st.caption("Trend: Look for uptrends (rising) → buy soon. Downtrends (falling) → wait.")

# ── PAGE 3: CORRELATION ────────────────────────────────────
elif page == "Correlation":
    st.subheader("Nickel ↔ Iron Ore Correlation")
    
    # Merge data
    data = nickel_hist.merge(iron_ore_hist, on="Date", how="inner")
    
    # Calculate correlation
    corr, _ = pearsonr(data["Nickel"], data["Iron"])
    col1, col2 = st.columns(2)
    if corr > 0.7:
        relationship = "Strong positive"
    elif corr > 0.3:
        relationship = "Moderate positive"
    elif corr > -0.3:
        relationship = "Weak / none"
    elif corr > -0.7:
        relationship = "Moderate negative"
    else:
        relationship = "Strong negative"

    col1.metric("Correlation", f"{corr:.3f}")
    col2.metric("Relationship", relationship)
    
     # Normalize both to 0-100 scale to show movement pattern
    data["Nickel_norm"] = (data["Nickel"] - data["Nickel"].min()) / (data["Nickel"].max() - data["Nickel"].min()) * 100
    data["IronOre_norm"] = (data["Iron"] - data["Iron"].min()) / (data["Iron"].max() - data["Iron"].min()) * 100
    
    fig = px.line(data, x="Date", y=["Nickel_norm", "IronOre_norm"],
                  title="Nickel vs Iron Ore: Normalized Price Movement (0-100 scale)",
                  labels={"value": "Normalized Price", "variable": "Commodity"},
                  color_discrete_map={"Nickel_norm": "#1f77b4", "IronOre_norm": "#ff7f0e"})
    
    fig.update_layout(height=500, hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)
    
    st.caption(f"Both normalized to 0-100 scale so you can see they move together. Correlation: {corr:.3f}")