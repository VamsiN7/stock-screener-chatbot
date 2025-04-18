import streamlit as st
from utils.data_loader import get_dow30_tickers, get_bulk_stock_data
from utils.lynch_scoring import score_lynch_criteria
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans
from numpy import unique, where


st.title("✅ Top Buy & Sell Recommendations")

tickers = get_dow30_tickers()
df = get_bulk_stock_data(tickers)
df["score"] = df.apply(lambda row: score_lynch_criteria(row)[0], axis=1)

st.subheader("📈 Top 10 Stocks to Buy")
top_buy = df.sort_values("score", ascending=False).head(10)
st.dataframe(top_buy[[
    "symbol", "peg_ratio", "pe_ratio", "de_ratio", "cash", "debt",
    "div_yield", "price_to_cashflow", "score"
]])

st.subheader("📉 Top 10 Stocks to Sell")
top_sell = df.sort_values("score", ascending=True).head(10)
st.dataframe(top_sell[[
    "symbol", "peg_ratio", "pe_ratio", "de_ratio", "cash", "debt",
    "div_yield", "price_to_cashflow", "score"
]])


# ----------------- Clustering Insights -----------------
st.markdown("---")
st.subheader("📈 Clustering: Stocks to Long vs Sell (K-Means)")

try:
    from sklearn.preprocessing import MinMaxScaler
    from sklearn.cluster import KMeans
    import plotly.express as px
    import numpy as np

    # Drop non-numeric/informative columns before clustering
    clustering_df = df.copy().set_index("symbol").fillna(0)

    # Drop these columns before clustering
    drop_cols = [
        'maxAge', 'currentPrice', 'targetHighPrice', 'targetLowPrice',
        'targetMeanPrice', 'targetMedianPrice', 'recommendationMean',
        'recommendationKey', 'numberOfAnalystOpinions', 'financialCurrency'
    ]
    clustering_df = clustering_df.drop(columns=[col for col in drop_cols if col in clustering_df.columns], errors='ignore')

    # Select only numeric columns for clustering
    X = clustering_df.select_dtypes(include=[np.number])

    # Scale features
    scaler = MinMaxScaler()
    X_scaled = scaler.fit_transform(X)

    # Run KMeans
    model = KMeans(n_clusters=4, random_state=100)
    cluster_labels = model.fit_predict(X_scaled) 

    # Add cluster assignments
    clustering_df["cluster"] = cluster_labels

    # Compute cluster means and sort to identify best/worst clusters
    cluster_mean_metric = clustering_df.groupby("cluster")[X.columns[2]].mean()
    best_cluster = cluster_mean_metric.idxmax()
    worst_cluster = cluster_mean_metric.idxmin()

    # Assign colors and labels
    clustering_df["cluster_label"] = clustering_df["cluster"].apply(lambda x: f"Cluster {x+1}")

    # Plot using Plotly
    fig = px.scatter(
        x=X_scaled[:, 0],
        y=X_scaled[:, 1],
        color=clustering_df["cluster_label"],
        hover_name=clustering_df.index,
        title="K-Means Clustering of Dow 30 Stocks",
        labels={"x": f"{X.columns[0]} (Scaled)", "y": f"{X.columns[1]} (Scaled)"}
    )
    fig.update_traces(marker=dict(size=10, line=dict(width=1, color='DarkSlateGrey')))
    fig.update_layout(height=600)
    st.plotly_chart(fig, use_container_width=True)

    # Recommendations
    long_candidates = clustering_df[clustering_df["cluster"] == best_cluster].index.tolist()
    sell_candidates = clustering_df[clustering_df["cluster"] == worst_cluster].index.tolist()

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### ✅ Suggested Long Candidates")
        st.write(long_candidates if long_candidates else "None found.")
    with col2:
        st.markdown("#### 🚫 Suggested Sell Candidates")
        st.write(sell_candidates if sell_candidates else "None found.")

except ModuleNotFoundError:
    st.error("Please install `scikit-learn` to use clustering features: `pip install scikit-learn`")
except Exception as e:
    st.error(f"Error in clustering analysis: {e}")