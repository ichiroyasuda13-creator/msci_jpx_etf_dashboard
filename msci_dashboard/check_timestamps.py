import yfinance as yf
from datetime import datetime

ticker = "2559.T"
print(f"Checking timestamps for {ticker}...")
stock = yf.Ticker(ticker)
info = stock.info

# Check for various timestamp keys
keys_to_check = [
    'regularMarketTime', 'postMarketTime', 'preMarketTime',
    'lastCapGain', 'lastDividendDate', 'date' # generic guess
]

print("--- TIMESTAMPS ---")
for k in keys_to_check:
    val = info.get(k)
    if val:
        try:
            # yfinance often sends unix timestamp
            readable = datetime.fromtimestamp(val)
            print(f"{k}: {val} -> {readable}")
        except:
             print(f"{k}: {val}")

print("\n--- PRICE/NAV ---")
print(f"Price: {info.get('regularMarketPreviousClose')}")
print(f"NAV: {info.get('navPrice')}")
