import pandas as pd
import yfinance as yf
import streamlit as st

@st.cache_data(ttl=86400)
def get_dow30_tickers():
    return [
        "AAPL", "AMGN", "AXP", "BA", "CAT", "CRM", "CSCO", "CVX", "DIS", "DOW",
        "GS", "HD", "HON", "IBM", "INTC", "JNJ", "JPM", "KO", "MCD", "MMM",
        "MRK", "MSFT", "NKE", "PG", "TRV", "UNH", "V", "VZ", "WBA", "WMT"
    ]

@st.cache_data(ttl=3600)
def get_stock_info(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info

    current_price = info.get("currentPrice")
    pe_ratio = info.get("trailingPE")

    # Manually patch missing P/E values
    if pe_ratio is None or pe_ratio == 0:
        if ticker == "BA":
            pe_ratio = 36.90
        elif ticker == "INTC":
            pe_ratio = 43.48
        elif ticker == "WBA":
            pe_ratio = 6.97

    peg_ratio = info.get("pegRatio")

    # Manual peg_ratio overrides for missing values
    peg_fallbacks = {
        "AMGN": 1.62,
        "BA": 2.94,
        "CSCO": 2.41,
        "DOW": 1.54,
        "IBM": 1.27,
        "INTC": 6.75,
        "JNJ": 2.39,
        "JPM": 1.25,
        "MCD": 2.44,
        "MMM": 2.15,
        "MRK": 1.43,
        "NKE": 2.59,
        "TRV": 1.04,
        "UNH": 1.62,
        "VZ": 0.91,
        "WBA": 1.71,
        "WMT": 2.23
    }
    if (peg_ratio is None or peg_ratio == 0) and ticker in peg_fallbacks:
        peg_ratio = peg_fallbacks[ticker]

    de_ratio = info.get("debtToEquity")
    if de_ratio is not None:
        de_ratio = round(de_ratio / 100, 4)

    free_cash_flow = info.get("freeCashflow")
    shares_outstanding = info.get("sharesOutstanding")
    earnings_growth = info.get("earningsGrowth")

    # PEG fallback 1: EPS CAGR via income_stmt
    if (peg_ratio is None or peg_ratio == 0):
        try:
            income_stmt = stock.income_stmt
            if "Net Income" in income_stmt.index and len(income_stmt.columns) >= 2 and shares_outstanding:
                net_income_latest = income_stmt.loc["Net Income"].iloc[0]
                net_income_base = income_stmt.loc["Net Income"].iloc[-1]
                n_years = len(income_stmt.columns) - 1

                if net_income_latest > 0 and net_income_base > 0:
                    eps_latest = net_income_latest / shares_outstanding
                    eps_base = net_income_base / shares_outstanding
                    eps_cagr = ((eps_latest / eps_base) ** (1 / n_years)) - 1
                    if eps_cagr > 0.01 and pe_ratio:
                        peg_ratio = round(pe_ratio / (eps_cagr * 100 if eps_cagr < 1 else eps_cagr), 2)
        except:
            pass 

    # PEG fallback 2: Use earningsGrowth field
    if (peg_ratio is None or peg_ratio == 0) and pe_ratio and earnings_growth and earnings_growth > 0.01:
        try:
            peg_ratio = round(pe_ratio / (earnings_growth * 100 if earnings_growth < 1 else earnings_growth), 2)
        except:
            peg_ratio = None

    fcf_per_share = (free_cash_flow / shares_outstanding) if (free_cash_flow and shares_outstanding) else None
    price_to_cashflow = (current_price / fcf_per_share) if fcf_per_share else None

    return {
        "symbol": ticker,
        "name": info.get("shortName", "N/A"),
        "current_price": current_price,
        "target_high_price": info.get("targetHighPrice"),
        "target_low_price": info.get("targetLowPrice"),
        "pe_ratio": pe_ratio,
        "peg_ratio": peg_ratio,
        "de_ratio": de_ratio,
        "cash": info.get("totalCash"),
        "debt": info.get("totalDebt"),
        "div_yield": info.get("dividendYield"),
        "free_cash_flow": free_cash_flow,
        "shares_outstanding": shares_outstanding,
        "price_to_cashflow": price_to_cashflow,
        "roe": info.get("returnOnEquity"),
        "roa": info.get("returnOnAssets"),
        "gross_margin": info.get("grossMargins"),
        "operating_margin": info.get("operatingMargins")
    }


@st.cache_data(ttl=3600)
def get_bulk_stock_data(tickers=None, limit=30):
    if tickers is None:
        tickers = get_dow30_tickers()

    data = []
    for t in tickers[:limit]:
        try:
            data.append(get_stock_info(t))
        except Exception:
            continue
    return pd.DataFrame(data)

# Get and save
df = get_bulk_stock_data()
df.to_excel("dowjones_lynch_project_data.xlsx", index=False)
