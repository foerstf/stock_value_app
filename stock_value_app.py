import time
import yfinance as yf
import streamlit as st
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Stock Market Value", page_icon="💹")

st.title("📈 Stock Market Value (Auto-Refresh)")

# --- Controls (persist via session_state) ---
colA, colB, colC = st.columns([2, 2, 2])
with colA:
    symbol = st.text_input("Ticker", value=st.session_state.get("symbol", "AAPL"), key="symbol")
with colB:
    shares = st.number_input("Shares", min_value=0, step=1, value=st.session_state.get("shares", 0), key="shares")
with colC:
    refresh_min = st.number_input("Refresh (minutes)", min_value=0.0, step=0.5, value=st.session_state.get("refresh_min", 5.0), key="refresh_min")

manual = st.button("Refresh now")

# --- Auto refresh (doesn't reset inputs) ---
interval_ms = int(st.session_state.refresh_min * 60_000) if st.session_state.refresh_min > 0 else 0
if interval_ms > 0:
    st_autorefresh(interval=interval_ms, key="auto_refresh")

# --- Fetch price helper ---
@st.cache_data(ttl=60)  # cache briefly to avoid hammering the endpoint
def fetch_price_latest_close(sym: str):
    if not sym:
        return None
    t = yf.Ticker(sym)
    hist = t.history(period="1d")
    if hist.empty:
        return None
    return float(hist["Close"].iloc[-1])

# Re-fetch when:
#  - manual button pressed
#  - autorefresh triggers a rerun (handled automatically)
#  - inputs change (built-in rerun)
price = fetch_price_latest_close(st.session_state.symbol.upper())

# --- Display ---
box = st.container()
if not st.session_state.symbol:
    box.warning("Enter a ticker.")
elif price is None:
    box.error("Invalid ticker or no price available.")
else:
    market_value = price * (st.session_state.shares or 0)
    box.markdown(f"**{st.session_state.symbol.upper()}**")
    box.metric(label="Last Price (delayed)", value=f"${price:,.2f}")
    box.metric(label="Market Value", value=f"${market_value:,.2f}")
    st.caption("Prices are typically delayed ~15 minutes.")

# Timestamp so you know it updated
st.write(f"Last update: {time.strftime('%Y-%m-%d %H:%M:%S')}")

# Small UX note
st.caption("Tip: Set Refresh (minutes) to 0 to disable auto-refresh.")
