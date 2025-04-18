def score_lynch_criteria(stock):
    score = 0
    reasons = []

    def safe_get(key):
        return stock.get(key, None)

    # 1. PEG Ratio < 1
    peg = safe_get("peg_ratio")
    if peg is not None and peg < 1:
        score += 1
        reasons.append("PEG < 1")

    # 2. P/E Ratio < 20
    pe = safe_get("pe_ratio")
    if pe is not None and pe < 20:
        score += 1
        reasons.append("P/E < 20")

    # 3. Debt/Equity < 0.5
    de = safe_get("de_ratio")
    if de is not None and de < 0.5:
        score += 1
        reasons.append("D/E < 0.5")

    # 4. Cash > Debt
    cash = safe_get("cash")
    debt = safe_get("debt")
    if cash is not None and debt is not None and cash > debt:
        score += 1
        reasons.append("Cash > Debt")

    # 5. Dividend Yield > 2%
    div = safe_get("div_yield")
    if div is not None and div > 0.02:
        score += 1
        reasons.append("Div Yield > 2%")

    # 6. Price to Cash Flow > 5
    pcf = safe_get("price_to_cashflow")
    if pcf is not None and pcf > 5:
        score += 1
        reasons.append("P/CF > 5")

    return score, reasons
