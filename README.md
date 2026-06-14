# Steel Commodity Price Tracker

## What This Project Does

Tracks live nickel and iron ore prices for real-time inventory decisions. Built for my family's stainless steel retail business in Vietnam.

Instead of checking WhatsApp supplier messages and guessing when to buy stock, they now have a data-driven alert system that shows:
- Live nickel price (updated hourly)
- 20-year price trends
- Nickel ↔ Iron ore correlation
- Buy/Wait/Hold recommendation

## Key Findings

**Nickel ↔ Iron Ore Correlation: 0.650**
- Moderate correlation means they move together but not perfectly
- When nickel rises 10%, iron ore usually rises ~6-7%
- Nickel is a leading indicator for iron ore movements

**Signal Logic**
- Nickel down 7%+ (7-day) → WAIT, prices falling further expected
- Nickel up 5%+ (7-day) → BUY NOW, supplier prices will rise in 4-8 weeks
- Nickel stable ±5% → HOLD, proceed with normal ordering

## Live Dashboard

[View live dashboard](https://metaltracker-cpktj7dq2fx2qhvyvgdpyw.streamlit.app/)

## Tech Stack

- **Data**: Metal Sentinel API (live nickel), investing.com (20-year history)
- **Analysis**: Pandas, SciPy (correlation)
- **Deployment**: Streamlit Cloud
- **Automation**: Python + Windows Task Scheduler (daily collection)

## How to Run Locally

```bash
pip install -r requirements.txt
streamlit run steel_tracker_app.py
```

## Daily Data Collection

The `scripts/daily_collector.py` runs automatically every day at 7pm (Windows Task Scheduler) and appends the day's nickel price to `data/nickel_daily.csv`.

## Future Enhancements

- Add chromium price tracking (18% of stainless steel cost)
- Currency risk modeling (VND/USD/CNY exchange rates)
- Supplier markup prediction
- Inventory optimization recommendations

## Project Story

Built this because my family's steel business in Vietnam makes buying decisions based on gut instinct. By tracking commodity prices and their correlations, they can now make data-driven decisions about when to stock up and when to wait — potentially saving thousands of dollars per year.
