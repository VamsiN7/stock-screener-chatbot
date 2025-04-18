# 📈 Peter Lynch Screener

A multi‑page **Streamlit** web application that lets you explore stocks through the legendary value‑investing lens of **Peter Lynch**.\
It pulls real‑time fundamentals with **Yahoo Finance**, crunches the numbers in Python, and presents them in an interactive dashboard that helps students and investors quickly see which companies look like “ten‑baggers”.

 

## ✨ Key Features

- **Home dashboard** with live Dow 30 price chart, moving averages, and historical context.
- **Stock Analysis** page that computes and visualises:
  - **PEG ratio** and growth metrics
  - Lynch’s **6 stock classifications** (Slow Grower, Stalwart, Fast Grower, Cyclical, Turnaround, Asset Play)
  - **21 Golden Rules** checklist with pass/fail badges
  - **Ten‑Bagger Potential** score derived from earnings growth and valuation spreads
- **Recommendations** page ranking tickers by a composite Lynch score for at‑a‑glance ideas.
- **Screener** to filter the Dow 30 (or any ticker list you supply) by PEG, P/E, dividend yield, and more.
- Caching with `st.cache_data` for snappy reloads and lower API usage.
- Built with **Plotly** for interactive charts and **Pandas** for data wrangling.

 

## 🛠️ Installation

```bash
# 1. Clone the repository
git clone https://github.com/your‑username/peter‑lynch‑screener.git
cd peter‑lynch‑screener

# 2. Create a virtual environment (optional but recommended)
python -m venv .venv
source .venv/bin/activate   # On Windows use .venv\\Scripts\\activate

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Launch Streamlit
streamlit run app.py
```

> **Python 3.9+** is recommended.\
> The main external packages are **streamlit**, **yfinance**, **pandas**, **plotly**, and **numpy**.

 

## 🚀 Usage

1. Open the browser tab that Streamlit prints (usually [http://localhost:8501](http://localhost:8501)).
2. Navigate with the left‑hand sidebar between **Home**, **Stock Analysis**, **Recommendations**, and **Screener**.
3. Select tickers, adjust date ranges, and toggle chart overlays to explore companies the Lynch way.
4. Hover over charts or click table rows for tool‑tips and deeper dives.

 

## 📂 Project Structure

```
.
├── app.py                  # Main entry; sets up sidebar & page routing
├── pages/
│   ├── 1_Home.py
│   ├── 2_Stock_Analysis.py
│   ├── 3_Recommendations.py
│   ├── 4_Screener.py
│   └── 5_Market_Insights.py   # (optional/experimental)
├── utils/
│   ├── data_loader.py      # Live data download & caching helpers
│   └── lynch_scoring.py    # Core PEG & Lynch‑rule calculations
└── README.md               # → You are here
```

> If you prefer flatter layouts, import paths can be adjusted in the page files.

 

## 🔎 How the Analysis Works

| Component                | Logic (high level)                                                                                                                                                |
| ------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **PEG Ratio**            | `PEG = P/E ÷ 5‑Y EPS Growth`; values **< 1** score best.                                                                                                          |
| **Lynch Class**          | Uses revenue growth, market‑cap, and cyclicality heuristics to tag stocks as *Slow Grower*, *Stalwart*, *Fast Grower*, *Cyclical*, *Turnaround*, or *Asset Play*. |
| **21 Golden Rules**      | Boolean checklist; each pass adds to an overall confidence %.                                                                                                     |
| **Ten‑Bagger Potential** | Combines PEG, earnings runway, and reinvestment rate to estimate upside probability (purely educational – **not investment advice**).                             |

See `utils/lynch_scoring.py` for the exact conditions and weights.

 

## 🌐 Data Sources & Disclaimer

Market data comes from **Yahoo Finance** via the `yfinance` Python package.\
All information is provided **as‑is for educational purposes**. This app is **not financial advice**; always do your own research before investing.

 

## 🤝 Contributing

Pull requests are welcome! If you have an idea for a new feature (e.g., custom watchlists, additional ratios, or alternative data sources), feel free to open an issue or PR.
