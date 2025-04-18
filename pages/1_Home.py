import streamlit as st 
st.set_page_config(page_title="Peter Lynch Screener", layout="wide") 
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from utils.data_loader import get_dow30_tickers, get_bulk_stock_data
from utils.lynch_scoring import score_lynch_criteria


st.title("🏠 Peter Lynch Screener")
st.write("")
st.write("")

# ---------------- Sidebar Controls -------------------
st.sidebar.header("📊 Chart Controls")
range_option = st.sidebar.selectbox("📅 Select Date Range", ["1d", "5d", "1mo", "6mo", "1y", "5y"])
show_ma = st.sidebar.checkbox("Show Moving Averages", value=True)

interval_map = {
    "1d": "5m",
    "5d": "5m",
    "1mo": "1h",
    "6mo": "1d",
    "1y": "1d",
    "5y": "1wk"
}
interval = interval_map[range_option]
stock = yf.Ticker("^DJI")
hist = stock.history(period=range_option, interval=interval)

# -------------------- KPI Metrics ----------------------
# -------------------- KPI Metrics (based on selected range) ----------------------
st.subheader("📊 Key Metrics")

latest_open = hist["Open"].iloc[0] if not hist.empty else "N/A"
latest_high = hist["High"].max() if not hist.empty else "N/A"
latest_low = hist["Low"].min() if not hist.empty else "N/A"
latest_close = hist["Close"].iloc[-1] if not hist.empty else "N/A"

# 52W data still uses static info (not affected by range)
info = stock.info
fifty_two_week_high = info.get("fiftyTwoWeekHigh", "N/A")
fifty_two_week_low = info.get("fiftyTwoWeekLow", "N/A")


kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric("Open (Today)", f"${round(latest_open, 2)}" if latest_open != "N/A" else "N/A")
kpi2.metric("High (Today)", f"${round(latest_high, 2)}" if latest_high != "N/A" else "N/A")
kpi3.metric("Low (Today)", f"${round(latest_low, 2)}" if latest_low != "N/A" else "N/A")

st.write("")
kpi4, kpi5, kpi6 = st.columns(3)
kpi4.metric("Close (Now)", f"${round(latest_close, 2)}" if latest_close != "N/A" else "N/A")
kpi5.metric("52W High", f"${fifty_two_week_high}")
kpi6.metric("52W Low", f"${fifty_two_week_low}")

# -------------------- Candlestick Chart ----------------------
st.write("")
st.subheader("📈 Dow Jones Chart")

# Moving Averages (optional)
if show_ma and not hist.empty:
    hist["MA20"] = hist["Close"].rolling(window=20).mean()
    hist["MA50"] = hist["Close"].rolling(window=50).mean()

# Plot
fig = go.Figure()

# Candlestick
fig.add_trace(go.Candlestick(
    x=hist.index,
    open=hist["Open"],
    high=hist["High"],
    low=hist["Low"],
    close=hist["Close"],
    name="Dow 30"
))

# Volume with green for up candles and red for down candles
volume_colors = ["green" if close >= open_ else "red"
                    for open_, close in zip(hist["Open"], hist["Close"])]

fig.add_trace(go.Bar(
    x=hist.index,
    y=hist["Volume"],
    name="Volume",
    marker=dict(color=volume_colors),
    yaxis="y2",
    opacity=0.4,
    showlegend=False
))


# Add MAs
if show_ma and "MA20" in hist.columns:
    fig.add_trace(go.Scatter(
        x=hist.index,
        y=hist["MA20"],
        mode="lines",
        name="20MA",
        line=dict(color="orange", width=1.5)
    ))
if show_ma and "MA50" in hist.columns:
    fig.add_trace(go.Scatter(
        x=hist.index,
        y=hist["MA50"],
        mode="lines",
        name="50MA",
        line=dict(color="green", width=1.5)
    ))

# Layout
fig.update_layout(
    title=f"Dow Jones – {range_option} Chart",
    xaxis_title="Date",
    yaxis_title="Price",
    yaxis2=dict(
        overlaying='y',
        side='right',
        title='Volume',
        showgrid=False
    ),
    xaxis_rangeslider_visible=False,
    height=600
)

st.plotly_chart(fig, use_container_width=True)

# -------------------- Dow Jones Description ----------------------
st.markdown("### ℹ️ About the Dow Jones Industrial Average")
st.write("""
The **Dow Jones Industrial Average (DJIA)** is one of the most recognized and influential stock market indices in the world. It consists of **30 large-cap, publicly traded companies** that are leaders in their respective industries, such as technology, finance, healthcare, and consumer goods.

Unlike other indices like the S&P 500 which are market-cap weighted, the DJIA is **price-weighted** — meaning stocks with a higher share price have a greater impact on the index’s movements. The DJIA is often used as a **barometer of the overall health** of the U.S. stock market and economy.
""")

# -------------------- Top Gainers / Losers ----------------------
st.write("")
st.write("")
dow_tickers = get_dow30_tickers()
changes = []

for ticker in dow_tickers:
    try:
        t = yf.Ticker(ticker)
        hist_today = t.history(period="1d", interval="1m")
        if not hist_today.empty:
            open_price = hist_today["Open"].iloc[0]
            close_price = hist_today["Close"].iloc[-1]
            percent_change = ((close_price - open_price) / open_price) * 100
            changes.append({
                "Ticker": ticker,
                "Company": t.info.get("shortName", "N/A"),
                "Open": round(open_price, 2),
                "Close": round(close_price, 2),
                "Change (%)": round(percent_change, 2)
            })
    except:
        continue

# Convert to DataFrame and sort
change_df = pd.DataFrame(changes)
gainers = change_df.sort_values("Change (%)", ascending=False).head(5).reset_index(drop=True)
losers = change_df.sort_values("Change (%)").head(5).reset_index(drop=True)

# Display with emojis/icons
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 🟢 ✅ Top 5 Gainers")
    gainers_display = gainers.copy()
    gainers_display["Change (%)"] = gainers_display["Change (%)"].apply(lambda x: f"🟢 +{x:.2f}%")
    st.dataframe(gainers_display, use_container_width=True)

with col2:
    st.markdown("#### 🔻 🔴 Top 5 Losers")
    losers_display = losers.copy()
    losers_display["Change (%)"] = losers_display["Change (%)"].apply(lambda x: f"🔻 {x:.2f}%")
    st.dataframe(losers_display, use_container_width=True)
