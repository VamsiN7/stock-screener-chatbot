import streamlit as st
st.set_page_config(page_title="🔍 Lynch Screener", layout="wide")
from utils.data_loader import get_dow30_tickers, get_bulk_stock_data
import pandas as pd
import yfinance as yf
import pandas as pd
from datetime import datetime

st.write("")
st.write("")
st.title("🔍 Screener")

# ----------------- Filter Row -----------------
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    peg_filter = st.checkbox("PEG Ratio < 1")
    pe_filter = st.checkbox("P/E Ratio < 20")

with col2:
    de_filter = st.checkbox("Debt/Equity < 0.5")
    cash_filter = st.checkbox("Cash > Debt")

with col3:
    div_filter = st.checkbox("Dividend Yield > 2%")
    pcf_filter = st.checkbox("Price to Cash Flow > 5")

with col4:
    gm_filter = st.checkbox("Gross Margin > 20%")
    om_filter = st.checkbox("Operating Margin > 10%")

with col5:
    roe_filter = st.checkbox("ROE > 10%")
    roa_filter = st.checkbox("ROA > 5%")

# ----------------- Load Data -----------------
tickers = get_dow30_tickers()
df = get_bulk_stock_data(tickers)

# ----------------- Apply Filters -----------------
def apply_filters(row):
    if peg_filter and (row["peg_ratio"] is None or row["peg_ratio"] >= 1): return False
    if pe_filter and (row["pe_ratio"] is None or row["pe_ratio"] >= 20): return False
    if de_filter and (row["de_ratio"] is None or row["de_ratio"] >= 0.5): return False
    if cash_filter and (row["cash"] is None or row["debt"] is None or row["cash"] <= row["debt"]): return False
    if div_filter and (row["div_yield"] is None or row["div_yield"] * 100 <= 2): return False
    if pcf_filter and (row["price_to_cashflow"] is None or row["price_to_cashflow"] <= 5): return False
    return True

filtered_df = df[df.apply(apply_filters, axis=1)] if any([
    peg_filter, pe_filter, de_filter, cash_filter, div_filter, pcf_filter
]) else df


st.markdown("### Results")

columns_to_show = [
    "name", "symbol", "peg_ratio", "pe_ratio", "de_ratio", "cash", "debt",
    "div_yield", "price_to_cashflow", "gross_margin", "operating_margin", "roe", "roa"
]

display_df = filtered_df[columns_to_show].copy()
display_df.columns = [
    "Name", "Symbol", "PEG Ratio", "P/E Ratio", "Debt/Equity", "Cash", "Debt",
    "Dividend Yield", "Price/Cash Flow", "Gross Margin", "Operating Margin", "ROE", "ROA"
]

# Round and format numeric columns
for col in ["PEG Ratio", "P/E Ratio", "Debt/Equity", "Dividend Yield", "Price/Cash Flow",
            "Gross Margin", "Operating Margin", "ROE", "ROA"]:
    display_df[col] = display_df[col].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "N/A")

for col in ["Cash", "Debt"]:
    display_df[col] = display_df[col].apply(lambda x: f"${x:,.0f}" if pd.notna(x) else "N/A")

# ----------------- Row Display Option -----------------
row_option = st.selectbox("Select how many rows to show at once", [5, 10, 30], index=1)

# Estimate row height (approx 35px per row + ~50px header)
row_height_px = 35
table_height = row_option * row_height_px + 50

st.dataframe(display_df, use_container_width=True, height=table_height)


# ----------------- Display Table -----------------
st.markdown("---")
st.title("Compare Stocks")

# ---------------------- UI Styling ----------------------
st.markdown("""
    <style>
        div[data-baseweb="select"] {
            background-color: #1e1e1e !important;
            border: 1px solid #333 !important;
            border-radius: 10px;
            padding: 10px;
        }
        .block-container {
            padding-top: 1rem;
        }
        label {
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("Compare up to four stocks by selecting symbols from the dropdown below:")

# ---------------------- Dropdowns ----------------------
dow30 = get_dow30_tickers()
cols = st.columns(4)
tickers = [cols[i].selectbox(f"Stock {i+1}", [""] + dow30, key=f"stock{i}") for i in range(4)]
selected_tickers = [t for t in tickers if t]

# ---------------------- Fetch & Organize Data ----------------------
def get_stock_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return {
            "Name": info.get("shortName", "N/A"),
            "Symbol": ticker,
            # Market & Valuation
            "Market Value": info.get("marketCap", "N/A"),
            "Enterprise Value": info.get("enterpriseValue", "N/A"),
            # Price Ratios
            "P/E": info.get("trailingPE", "N/A"),
            "Forward P/E": info.get("forwardPE", "N/A"),
            "Price to FCF": info.get("priceToFreeCashflows", "N/A"),
            "Price to Book": info.get("priceToBook", "N/A"),
            "Price to Sales": info.get("priceToSalesTrailing12Months", "N/A"),
            "EV/EBITDA": info.get("enterpriseToEbitda", "N/A"),
            # Earnings
            "EPS": info.get("trailingEps", "N/A"),
            "EPS Growth": info.get("earningsGrowth", 0) * 100 if info.get("earningsGrowth") else "N/A",
            # Dividend
            "Dividend Yield": round(info.get("dividendYield", 0) * 100, 2) if info.get("dividendYield") else "N/A",
            # Margin
            "Gross Margin": round(info.get("grossMargins", 0) * 100, 2) if info.get("grossMargins") else "N/A",
            "Operating Margin": round(info.get("operatingMargins", 0) * 100, 2) if info.get("operatingMargins") else "N/A",
            "Profit Margin": round(info.get("profitMargins", 0) * 100, 2) if info.get("profitMargins") else "N/A",
            # Return
            "Return on Assets": round(info.get("returnOnAssets", 0) * 100, 2) if info.get("returnOnAssets") else "N/A",
            "Return on Equity": round(info.get("returnOnEquity", 0) * 100, 2) if info.get("returnOnEquity") else "N/A",
            # Balance Sheet
            "Inventory": info.get("inventory", "N/A"),
            "Free Cash Flow": info.get("freeCashflow", "N/A"),
            # Profile
            "Sector": info.get("sector", "N/A"),
            "Industry": info.get("industry", "N/A"),
            "CEO": info.get("companyOfficers", [{}])[0].get("name", "N/A") if info.get("companyOfficers") else "N/A",
        }
    except Exception as e:
        return {"Symbol": ticker, "Error": str(e)}

# ---------------------- Display Comparison ----------------------
if selected_tickers:
    all_data = [get_stock_data(t) for t in selected_tickers]
    df = pd.DataFrame(all_data).set_index("Symbol").T

    st.markdown("## 🧾 Comparison Breakdown")

    sections = {
        "📈 Market Value": ["Market Value", "Enterprise Value"],
        "💹 Price Ratios": ["P/E", "Forward P/E", "Price to FCF", "Price to Book", "Price to Sales", "EV/EBITDA"],
        "📊 Earnings": ["EPS", "EPS Growth"],
        "💸 Dividend": ["Dividend Yield"],
        "📐 Margin": ["Gross Margin", "Operating Margin", "Profit Margin"],
        "🧮 Returns": ["Return on Assets", "Return on Equity"],
        "📄 Balance Sheet": ["Inventory", "Free Cash Flow"],
        "🏢 Company Profile": ["Name", "Sector", "Industry", "CEO"]
    }

    for section, fields in sections.items():
        with st.expander(section, expanded=False):
            display = df.loc[df.index.intersection(fields)]
            st.dataframe(display, use_container_width=True)
else:
    st.info("Select at least one stock to compare.")