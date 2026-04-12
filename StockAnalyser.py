import json
import os
import csv
import datetime

# ── yfinance ───────────────────────
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False

# ── DATA STORE ───────────────────────────────────────────────

STOCK_DATA = {
    "HAL":   {"name": "Hindustan Aeronautics Ltd",    "sector": "Defence",     "price": 4200,  "eps": 98,   "high_52w": 4800,  "low_52w": 2900,  "symbol_yf": "HAL.NS"},
    "BEL":   {"name": "Bharat Electronics Ltd",       "sector": "Defence",     "price": 290,   "eps": 8.5,  "high_52w": 340,   "low_52w": 170,   "symbol_yf": "BEL.NS"},
    "PARAS": {"name": "Paras Defence & Space Tech",   "sector": "Defence",     "price": 1050,  "eps": 14,   "high_52w": 1300,  "low_52w": 680,   "symbol_yf": "PARAS.NS"},
    "MTAR":  {"name": "MTAR Technologies",            "sector": "Defence",     "price": 1800,  "eps": 32,   "high_52w": 2200,  "low_52w": 1200,  "symbol_yf": "MTARTECH.NS"},
    "DATAP": {"name": "Data Patterns India",          "sector": "Defence",     "price": 2900,  "eps": 55,   "high_52w": 3500,  "low_52w": 1800,  "symbol_yf": "DATAPATTNS.NS"},
    "INFY":  {"name": "Infosys Ltd",                  "sector": "IT",          "price": 1780,  "eps": 63,   "high_52w": 1950,  "low_52w": 1350,  "symbol_yf": "INFY.NS"},
    "TCS":   {"name": "Tata Consultancy Services",    "sector": "IT",          "price": 4100,  "eps": 120,  "high_52w": 4450,  "low_52w": 3200,  "symbol_yf": "TCS.NS"},
    "HDFC":  {"name": "HDFC Bank",                    "sector": "Banking",     "price": 1680,  "eps": 88,   "high_52w": 1800,  "low_52w": 1400,  "symbol_yf": "HDFCBANK.NS"},
    "RELI":  {"name": "Reliance Industries",          "sector": "Conglomerate","price": 2950,  "eps": 96,   "high_52w": 3200,  "low_52w": 2200,  "symbol_yf": "RELIANCE.NS"},
    "MM":    {"name": "Mahindra & Mahindra",          "sector": "Auto",        "price": 2800,  "eps": 78,   "high_52w": 3200,  "low_52w": 1800,  "symbol_yf": "M&M.NS"},
}

PORTFOLIO_FILE = "my_portfolio.json"

# ── HELPERS ──────────────────────────────────────────────────

def load_portfolio():
    if os.path.exists(PORTFOLIO_FILE):
        with open(PORTFOLIO_FILE, "r") as f:
            return json.load(f)
    return {}

def save_portfolio(portfolio):
    with open(PORTFOLIO_FILE, "w") as f:
        json.dump(portfolio, f, indent=2)

def divider(char="─", length=60):
    print(char * length)

def header(title):
    divider("═")
    print(f"  {title}")
    divider("═")

def calculate_pe(price, eps):
    if eps <= 0:
        return "N/A"
    return round(price / eps, 2)

# ── FEATURE 1: VIEW ALL STOCKS ───────────────────────────────

def view_all_stocks():
    header("ALL STOCKS IN DATABASE")
    print(f"  {'Ticker':<8} {'Company':<34} {'Sector':<15} {'Price (₹)':>10}  {'P/E':>7}")
    divider()
    for ticker, d in STOCK_DATA.items():
        pe = calculate_pe(d["price"], d["eps"])
        pe_str = f"{pe}x" if pe != "N/A" else "N/A"
        print(f"  {ticker:<8} {d['name']:<34} {d['sector']:<15} ₹{d['price']:>8,}  {pe_str:>7}")
    divider()
    print(f"  Total stocks: {len(STOCK_DATA)}\n")

# ── FEATURE 2: STOCK DEEP DIVE ───────────────────────────────

def stock_deep_dive():
    header("STOCK DEEP DIVE")
    ticker = input("  Enter ticker symbol (e.g. HAL, BEL): ").upper().strip()

    if ticker not in STOCK_DATA:
        print(f"\n  ❌ '{ticker}' not found. Use option [1] to see all tickers.\n")
        return

    s = STOCK_DATA[ticker]
    pe = calculate_pe(s["price"], s["eps"])
    if s["high_52w"] == s["low_52w"]:
        week_range_pct = 0
    else:
        week_range_pct = round(((s["price"] - s["low_52w"]) / (s["high_52w"] - s["low_52w"])) * 100, 1)

 # Visual 52-week bar
    bar_len = 30
    filled = int((week_range_pct / 100) * bar_len)
    bar = "█" * filled + "░" * (bar_len - filled)

    print(f"""
  Company       : {s['name']}
  Sector        : {s['sector']}
  ──────────────────────────────────────────────────
  Current Price : ₹{s['price']:,}
  52-Week High  : ₹{s['high_52w']:,}
  52-Week Low   : ₹{s['low_52w']:,}
  52W Position  : [{bar}] {week_range_pct}%
  ──────────────────────────────────────────────────
  EPS           : ₹{s['eps']}
  P/E Ratio     : {pe}x
  ──────────────────────────────────────────────────""")

    if pe != "N/A":
        if pe < 15:
            signal = "🟢 Possibly UNDERVALUED — low P/E"
        elif pe < 30:
            signal = "🟡 FAIRLY VALUED — moderate P/E"
        else:
            signal = "🔴 Possibly OVERVALUED — high P/E"
        print(f"  Valuation     : {signal}")

    print()

# ── FEATURE 3: SECTOR COMPARISON ─────────────────────────────

def sector_comparison():
    header("SECTOR COMPARISON")

    sectors = {}
    for ticker, data in STOCK_DATA.items():
        sec = data["sector"]
        pe = calculate_pe(data["price"], data["eps"])
        if sec not in sectors:
            sectors[sec] = {"stocks": [], "pe_values": [], "prices": []}
        sectors[sec]["stocks"].append(ticker)
        sectors[sec]["prices"].append(data["price"])
        if pe != "N/A":
            sectors[sec]["pe_values"].append(pe)

    print(f"  {'Sector':<16} {'Stocks':<28} {'Avg P/E':>8}  {'# Stocks':>8}")
    divider()
    for sector, info in sectors.items():
        avg_pe = round(sum(info["pe_values"]) / len(info["pe_values"]), 1) if info["pe_values"] else "N/A"
        stocks_str = ", ".join(info["stocks"])
        print(f"  {sector:<16} {stocks_str:<28} {str(avg_pe):>7}x  {len(info['stocks']):>8}")
    divider()
    print()

# ── FEATURE 4: PORTFOLIO MANAGER ─────────────────────────────

def portfolio_manager():
    header("MY PORTFOLIO")
    portfolio = load_portfolio()

    print("  [A] Add stock   [R] Remove stock   [V] View portfolio   [B] Back")
    choice = input("  Choice: ").upper().strip()

    if choice == "A":
        ticker = input("  Ticker to add: ").upper().strip()
        if ticker not in STOCK_DATA:
            print("  ❌ Ticker not found.\n")
            return
        try:
            qty = int(input(f"  Quantity of {ticker}: "))
            buy_price = float(input(f"  Your buy price (₹): "))
        except ValueError:
            print("  ❌ Invalid number entered.\n")
            return
        if qty <= 0 or buy_price <= 0:
            print("  ❌ Quantity and price must be positive numbers.\n")
            return
        portfolio[ticker] = {"qty": qty, "buy_price": buy_price}
        save_portfolio(portfolio)
        print(f"  ✅ {ticker} added to portfolio.\n")

    elif choice == "R":
        ticker = input("  Ticker to remove: ").upper().strip()
        if ticker in portfolio:
            del portfolio[ticker]
            save_portfolio(portfolio)
            print(f"  ✅ {ticker} removed.\n")
        else:
            print("  ❌ Not in portfolio.\n")

    elif choice == "V":
        if not portfolio:
            print("  📭 Portfolio is empty. Add some stocks first!\n")
            return

        total_invested = 0
        total_current  = 0

        print(f"\n  {'Ticker':<8} {'Qty':>5} {'Buy ₹':>10} {'Now ₹':>10} {'P&L ₹':>12} {'Return':>8}")
        divider()
        for ticker, info in portfolio.items():
            if ticker not in STOCK_DATA:
                print(f"  {ticker:<8} — stock data not found, skipping.")
                continue
            current     = STOCK_DATA[ticker]["price"]
            invested    = info["qty"] * info["buy_price"]
            current_val = info["qty"] * current
            pnl         = current_val - invested
            ret         = round((pnl / invested) * 100, 2)
            arrow       = "▲" if pnl >= 0 else "▼"
            total_invested += invested
            total_current  += current_val
            print(f"  {ticker:<8} {info['qty']:>5} ₹{info['buy_price']:>8,.0f} ₹{current:>8,} {arrow}₹{abs(pnl):>9,.0f} {ret:>+7.2f}%")

        divider()
        total_pnl = total_current - total_invested
        total_ret = round((total_pnl / total_invested) * 100, 2) if total_invested else 0
        arrow     = "▲" if total_pnl >= 0 else "▼"
        print(f"  {'TOTAL':<8} {'':>5} ₹{total_invested:>8,.0f} ₹{total_current:>8,.0f} {arrow}₹{abs(total_pnl):>9,.0f} {total_ret:>+7.2f}%")
        print()

# ── FEATURE 5: GENERATE RESEARCH REPORT ──────────────────────

def generate_report():
    header("GENERATE STOCK RESEARCH REPORT")
    ticker = input("  Enter ticker for report (e.g. HAL): ").upper().strip()

    if ticker not in STOCK_DATA:
        print("  ❌ Ticker not found.\n")
        return

    s        = STOCK_DATA[ticker]
    pe       = calculate_pe(s["price"], s["eps"])
    date_str = datetime.datetime.now().strftime("%d %B %Y")

    if pe != "N/A":
        if pe < 15:
            recommendation = "BUY"
            rationale = "Trading at a low P/E multiple — potential undervaluation relative to earnings."
        elif pe < 30:
            recommendation = "HOLD"
            rationale = "Fairly valued at current levels. Monitor for earnings growth catalysts."
        else:
            recommendation = "AVOID / WAIT"
            rationale = "Elevated P/E suggests growth is priced in. High risk of correction."
    else:
        recommendation = "INSUFFICIENT DATA"
        rationale      = "EPS data unavailable for P/E valuation."

    if s["high_52w"] == s["low_52w"]:
        week_range_pct = 0
    else:
        week_range_pct = round(((s["price"] - s["low_52w"]) / (s["high_52w"] - s["low_52w"])) * 100, 1)

    report = f"""
╔══════════════════════════════════════════════════════════╗
  EQUITY RESEARCH NOTE — {date_str}
  Analyst: [Your Name]  |  For Educational Use Only
╚══════════════════════════════════════════════════════════╝

  COMPANY   : {s['name']} ({ticker})
  SECTOR    : {s['sector']}
  CMP       : ₹{s['price']:,}

── VALUATION METRICS ────────────────────────────────────────
  EPS          : ₹{s['eps']}
  P/E Ratio    : {pe}x
  52W High     : ₹{s['high_52w']:,}
  52W Low      : ₹{s['low_52w']:,}
  52W Position : {week_range_pct}% above 52-week low

── RECOMMENDATION ───────────────────────────────────────────
  Rating    : ★ {recommendation}
  Rationale : {rationale}

── RISK FACTORS ─────────────────────────────────────────────
  • Government policy changes affecting defence budgets
  • Competition from private entrants (Adani Defence, Tata)
  • Global supply chain and component shortages
  • Currency risk on imported components
  • Regulatory / ITAR export control changes

── DISCLAIMER ───────────────────────────────────────────────
  This note is for educational purposes only and does not
  constitute financial advice. Always do your own research.
════════════════════════════════════════════════════════════
"""
    print(report)

    save = input("  Save this report to a .txt file? (y/n): ").lower()
    if save == "y":
        filename = f"report_{ticker}_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"  ✅ Saved as '{filename}'\n")

# ── FEATURE 6: ADD CUSTOM STOCK ──────────────────────────────

def add_custom_stock():
    header("ADD CUSTOM STOCK")
    print("  Add any stock not in the default database.\n")
    try:
        ticker    = input("  Ticker symbol     : ").upper().strip()
        name      = input("  Company name      : ").strip()
        sector    = input("  Sector            : ").strip()
        price     = float(input("  Current price (₹) : "))
        eps       = float(input("  EPS (₹)           : "))
        high      = float(input("  52-week high (₹)  : "))
        low       = float(input("  52-week low (₹)   : "))
        symbol_yf = input("  Yahoo Finance symbol (e.g. HAL.NS) [optional]: ").strip()
    except ValueError:
        print("  ❌ Invalid input. Please enter numbers for price/EPS/high/low.\n")
        return

    STOCK_DATA[ticker] = {
        "name": name, "sector": sector,
        "price": price, "eps": eps,
        "high_52w": high, "low_52w": low,
        "symbol_yf": symbol_yf if symbol_yf else ""
    }
    print(f"  ✅ {ticker} — {name} added for this session.\n")

# ── FEATURE 7: LIVE PRICE UPDATE (yfinance) ──────────────────

def live_price_update():
    header("LIVE PRICE UPDATE  (via yfinance)")

    if not YFINANCE_AVAILABLE:
        print("  ❌ yfinance is not installed.")
        print("  Run:  pip install yfinance")
        print("  Then restart the programme.\n")
        return

    print("  Options:")
    print("  [1] Update a single stock")
    print("  [2] Update ALL stocks in database")
    choice = input("  Choice: ").strip()

    if choice == "1":
        ticker = input("  Enter ticker (e.g. HAL): ").upper().strip()
        if ticker not in STOCK_DATA:
            print("  ❌ Ticker not found.\n")
            return
        _fetch_and_update([ticker])

    elif choice == "2":
        tickers_with_symbol = [t for t, d in STOCK_DATA.items() if d.get("symbol_yf")]
        if not tickers_with_symbol:
            print("  ❌ No Yahoo Finance symbols found in database.\n")
            return
        print(f"\n  Fetching live data for {len(tickers_with_symbol)} stocks...\n")
        _fetch_and_update(tickers_with_symbol)
    else:
        print("  ❌ Invalid option.\n")

def _fetch_and_update(tickers):
    """Fetch live price + 52w high/low from Yahoo Finance and update STOCK_DATA."""
    updated = 0
    failed  = []

    for ticker in tickers:
        symbol = STOCK_DATA[ticker].get("symbol_yf", "")
        if not symbol:
            print(f"  ⚠  {ticker} — no Yahoo Finance symbol set, skipping.")
            failed.append(ticker)
            continue
        try:
            info = yf.Ticker(symbol).fast_info
            live_price = round(info.last_price, 2)
            high_52w   = round(info.year_high, 2)
            low_52w    = round(info.year_low, 2)

            old_price = STOCK_DATA[ticker]["price"]
            STOCK_DATA[ticker]["price"]    = live_price
            STOCK_DATA[ticker]["high_52w"] = high_52w
            STOCK_DATA[ticker]["low_52w"]  = low_52w

            change     = round(live_price - old_price, 2)
            change_pct = round((change / old_price) * 100, 2) if old_price else 0
            arrow      = "▲" if change >= 0 else "▼"
            print(f"  ✅ {ticker:<8} ₹{live_price:>8,}  {arrow} ₹{abs(change):.2f} ({change_pct:+.2f}% vs stored)")
            updated += 1

        except Exception as e:
            print(f"  ❌ {ticker:<8} Failed — {e}")
            failed.append(ticker)

    print(f"\n  Done. Updated: {updated}  |  Failed: {len(failed)}")
    if failed:
        print(f"  Failed tickers: {', '.join(failed)}")
    print()

# ── FEATURE 8: EXPORT PORTFOLIO TO CSV ───────────────────────

def export_portfolio_csv():
    header("EXPORT PORTFOLIO TO CSV")
    portfolio = load_portfolio()

    if not portfolio:
        print("  📭 Portfolio is empty. Nothing to export.\n")
        return

    date_str = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"portfolio_export_{date_str}.csv"

    rows = []
    total_invested = 0
    total_current  = 0

    for ticker, info in portfolio.items():
        if ticker not in STOCK_DATA:
            continue
        s           = STOCK_DATA[ticker]
        current     = s["price"]
        invested    = info["qty"] * info["buy_price"]
        current_val = info["qty"] * current
        pnl         = current_val - invested
        ret         = round((pnl / invested) * 100, 2) if invested else 0
        pe          = calculate_pe(current, s["eps"])

        total_invested += invested
        total_current  += current_val

        rows.append({
            "Ticker":          ticker,
            "Company":         s["name"],
            "Sector":          s["sector"],
            "Qty":             info["qty"],
            "Buy Price (INR)": info["buy_price"],
            "CMP (INR)":       current,
            "Invested (INR)":  round(invested, 2),
            "Current Val (INR)": round(current_val, 2),
            "P&L (INR)":       round(pnl, 2),
            "Return (%)":      ret,
            "P/E Ratio":       pe,
            "52W High":        s["high_52w"],
            "52W Low":         s["low_52w"],
        })

    # Summary row
    total_pnl = total_current - total_invested
    total_ret = round((total_pnl / total_invested) * 100, 2) if total_invested else 0
    rows.append({
        "Ticker":            "TOTAL",
        "Company":           "─────────",
        "Sector":            "",
        "Qty":               "",
        "Buy Price (INR)":   "",
        "CMP (INR)":         "",
        "Invested (INR)":    round(total_invested, 2),
        "Current Val (INR)": round(total_current, 2),
        "P&L (INR)":         round(total_pnl, 2),
        "Return (%)":        total_ret,
        "P/E Ratio":         "",
        "52W High":          "",
        "52W Low":           "",
    })

    fieldnames = [
        "Ticker", "Company", "Sector", "Qty",
        "Buy Price (INR)", "CMP (INR)", "Invested (INR)",
        "Current Val (INR)", "P&L (INR)", "Return (%)",
        "P/E Ratio", "52W High", "52W Low"
    ]

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"  ✅ Portfolio exported to '{filename}'")
    print(f"  📊 Open it in Excel or Google Sheets for further analysis.\n")

# ── MAIN MENU ─────────────────────────────────────────────────

def main():
    yf_status = "✅ live prices ON" if YFINANCE_AVAILABLE else "⚠  offline mode (pip install yfinance)"

    while True:
        header(f"DEFENCE & EQUITY SECTOR ANALYSER  [{yf_status}]")
        print("  [1] View All Stocks")
        print("  [2] Stock Deep Dive")
        print("  [3] Sector Comparison")
        print("  [4] My Portfolio")
        print("  [5] Generate Research Report")
        print("  [6] Add Custom Stock")
        print("  [7] Live Price Update")
        print("  [8] Export Portfolio to CSV")
        print("  [0] Exit")
        divider()
        choice = input("  Select option: ").strip()

        if   choice == "1": view_all_stocks()
        elif choice == "2": stock_deep_dive()
        elif choice == "3": sector_comparison()
        elif choice == "4": portfolio_manager()
        elif choice == "5": generate_report()
        elif choice == "6": add_custom_stock()
        elif choice == "7": live_price_update()
        elif choice == "8": export_portfolio_csv()
        elif choice == "0":
            print("\n  Good trading. Stay curious. 📈\n")
            break
        else:
            print("  ❌ Invalid option. Try again.\n")

if __name__ == "__main__":
    main()
