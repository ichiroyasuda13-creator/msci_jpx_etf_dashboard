import yfinance as yf
import pandas as pd

ticker = "2559.T" # MAXIS ACWI
print(f"Checking data for {ticker}...")
stock = yf.Ticker(ticker)

# 1. Check get_shares_full (Historical Shares Outstanding)
try:
    shares = stock.get_shares_full(start="2024-01-01")
    print("\n--- HISTORICAL SHARES ---")
    if not shares.empty:
        print(shares.head())
        print(f"Count: {len(shares)}")
    else:
        print("Shares history is empty.")
except Exception as e:
    print(f"Error fetching shares: {e}")

# 2. Check metadata
info = stock.info
print(f"\nTotal Assets (Current): {info.get('totalAssets')}")
print(f"Shares Outstanding (Current): {info.get('sharesOutstanding')}")
