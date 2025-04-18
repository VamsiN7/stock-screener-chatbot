import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans
from numpy import unique, where
from utils.data_loader import get_dow30_tickers, get_bulk_stock_data
from utils.lynch_scoring import score_lynch_criteria

st.set_page_config(page_title="🧠 Market Insights", layout="wide")
st.title("🧠 Market Insights (Dow 30)")

tickers = get_dow30_tickers()
df = get_bulk_stock_data(tickers)
df["score"] = df.apply(lambda row: score_lynch_criteria(row)[0], axis=1)

# ----------------- Lynch Score Histogram -----------------
st.markdown("### 📊 Lynch Score Distribution")
fig1 = px.histogram(df, x="score", nbins=6, title="Lynch Score Histogram", labels={"score": "Lynch Score"})
fig1.update_layout(height=400, bargap=0.2)
st.plotly_chart(fig1, use_container_width=True)

# ----------------- Financial Correlations -----------------
st.markdown("---")
st.markdown("### 📌 Financial Metric Correlations")

metrics_df = df[[
    "peg_ratio", "pe_ratio", "de_ratio", "cash", "debt", "div_yield",
    "price_to_cashflow", "roe", "roa"
]].dropna()

fig2 = px.imshow(metrics_df.corr(), text_auto=True, aspect="auto",
                 color_continuous_scale="RdBu_r", title="Correlation Heatmap")
fig2.update_layout(height=500)
st.plotly_chart(fig2, use_container_width=True)

# ----------------- Top 10 Lynch Scorers -----------------
st.markdown("---")
st.markdown("### 🏆 Top 10 Lynch Scorers")
st.dataframe(df.sort_values("score", ascending=False).head(10), use_container_width=True)



