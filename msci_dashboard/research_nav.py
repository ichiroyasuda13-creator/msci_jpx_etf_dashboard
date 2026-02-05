import yfinance as yf
import pandas as pd

# Test Ticker: 2559.T (MAXIS ACWI)
ticker = "2559.T"
print(f"Fetching info for {ticker}...")
stock = yf.Ticker(ticker)

# 1. Check Info dictionary for NAV-related fields
info = stock.info
print("\n--- INFO DICT KEYS (containing 'nav' or 'net') ---")
for k in info.keys():
    if 'nav' in k.lower() or 'net' in k.lower():
        print(f"{k}: {info[k]}")

# 2. Check for navPrice
print(f"\nnavPrice: {info.get('navPrice')}")

# 3. Check History for 'Capital Gains' or other events that *might* imply NAV (unlikely)
hist = stock.history(period="1mo")
print("\n--- HISTORY COLUMNS ---")
print(hist.columns)

# 4. Check if a "^" symbol exists (sometimes NAV is Ticker^NAV, though rare for JP)
nav_ticker_guess = "2559.T^NAV" 
# This is usually not valid for JP, but for US it is.
