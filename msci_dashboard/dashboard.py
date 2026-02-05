# --- STEP 1: INSTALL LIBRARIES (If needed) ---
# Note: In a standard project structure, we use requirements.txt 
# and install via 'pip install -r requirements.txt'
# I am keeping the imports but removing the auto-installer for cleaner execution in this script.

try:
    import yfinance
    import plotly
except ImportError:
    print("Libraries missing. Please run: pip install -r requirements.txt")
    exit(1)

# --- STEP 2: DASHBOARD CODE ---
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf
from datetime import datetime, timedelta

# 1. Full List of JPX MSCI ETFs
# ---------------------------------------------------------
msci_tickers = {
    # --- GLOBAL & REGIONAL ---
    "Global (MSCI ACWI)": "2559.T",
    "Global ex-JP (MSCI ACWI ex-JP)": "1554.T",
    "Dev Mkts (MSCI Kokusai)": "1550.T",
    "Dev Mkts (MSCI Kokusai) #2": "1680.T",   # Added from PDF
    "Dev Mkts Unhedged (MSCI Kokusai)": "2513.T",
    "Dev Mkts ex-JP (MSCI Core)": "1657.T",
    "Emerging (MSCI EM)": "1681.T",
    "Emerging (MSCI EM IMI)": "1658.T",
    "Emerging Unhedged (MSCI EM)": "2520.T",
    "Saudi Arabia (MSCI Saudi)": "273A.T",    # Note: Very new listing

    # --- JAPAN STRATEGY / ESG ---
    "Japan High Div (MSCI)": "1478.T",
    "Japan Min Vol (MSCI)": "1477.T",
    "Japan High Div Low Vol (MSCI)": "1399.T",
    "Japan ESG Select (MSCI)": "1653.T",
    "Japan SRI (MSCI)": "2851.T",
    "Japan Women (MSCI WIN)": "1652.T",
    "Japan Women Select (MSCI)": "2518.T",
    "Japan Human/Phys Inv (MSCI)": "1479.T",
    "Japan Governance (MSCI)": "2636.T",
    "Japan Country Select (MSCI)": "2643.T",
    "Japan Climate Change (MSCI)": "2848.T",
    "Japan Climate Action (MSCI)": "2250.T",
    "Japan Climate Select (MSCI)": "294A.T",
    "Japan SuperDiv (MSCI)": "2564.T",
    "Japan Cash Flow King (MSCI)": "234A.T",

    # --- HEDGED / SPECIALTY ---
    "Dev Mkts Hedged (MSCI Kokusai)": "2514.T",
    "Japan Long/Short (MSCI)": "1490.T",
}

# 2. Data Fetching Engine
# ---------------------------------------------------------
def get_dashboard_data(ticker_dict):
    price_data = {}
    valuation_rows = []
    
    # Fetch data starting 400 days ago to ensure we have a full 1-Year return
    start_date = datetime.now() - timedelta(days=400) 

    print(f"Fetching data for {len(ticker_dict)} MSCI ETFs from JPX...")
    print("Note: New listings (like 234A) may have missing data.")
    
    for name, ticker in ticker_dict.items():
        try:
            stock = yf.Ticker(ticker)
            
            # A. Price History
            hist = stock.history(start=start_date)
            
            if not hist.empty:
                # Store closing prices
                price_data[name] = hist['Close']
                
                # B. Fundamentals (Valuations)
                info = stock.info
                
                # Calculate YTD Return manually
                ytd_start_df = hist[hist.index.year == datetime.now().year]
                if not ytd_start_df.empty:
                    ytd_start_price = ytd_start_df['Close'].iloc[0]
                    current_price = hist['Close'].iloc[-1]
                    ytd_ret = ((current_price - ytd_start_price) / ytd_start_price) * 100
                else:
                    ytd_ret = 0.0

                valuation_rows.append({
                    "Index Name": name,
                    "Ticker": ticker,
                    "Price (JPY)": hist['Close'].iloc[-1],
                    "YTD %": round(ytd_ret, 1),
                    # Handle missing fundamental data gracefully
                    "P/E": info.get('trailingPE', None),
                    "P/B": info.get('priceToBook', None),
                    "Yield %": round(info.get('yield', 0) * 100, 2) if info.get('yield') else None
                })
        except Exception as e:
            # Just print error and continue, don't crash
            print(f" > Skipped {name} ({ticker}): {e}")

    if not valuation_rows:
        print("No valuation data collected.")
        return pd.DataFrame(), pd.DataFrame()

    return pd.DataFrame(price_data), pd.DataFrame(valuation_rows).set_index("Index Name")

# Run the fetch
df_prices, df_valuations = get_dashboard_data(msci_tickers)

# 3. Calculate Performance Metrics (1M, 3M, 1Y)
# ---------------------------------------------------------
def calculate_metrics(df_prices):
    metrics = []
    for col in df_prices.columns:
        series = df_prices[col]
        # Percentage change periods (assuming ~21 trading days/month)
        ret_1m = series.pct_change(periods=21).iloc[-1] * 100
        ret_3m = series.pct_change(periods=63).iloc[-1] * 100
        
        # 1Y Return (handle cases where ETF is new and has <252 days of data)
        if len(series) >= 252:
            ret_1y = series.pct_change(periods=252).iloc[-1] * 100
        else:
            ret_1y = None 
        
        metrics.append({
            "Index Name": col,
            "1M %": round(ret_1m, 1),
            "3M %": round(ret_3m, 1),
            "1Y %": round(ret_1y, 1) if ret_1y else None
        })
    return pd.DataFrame(metrics).set_index("Index Name")

if not df_prices.empty:
    df_perf = calculate_metrics(df_prices)
    # Merge Price Performance with Valuations
    df_final = df_valuations.join(df_perf)

    # 4. Visualization: Performance Bar Chart
    # ---------------------------------------------------------
    def plot_msci_performance(df):
        # Sort by YTD performance for the chart
        df_sorted = df.sort_values('YTD %', ascending=True)
        
        fig = go.Figure()
        
        # 1 Year Bar (Green)
        fig.add_trace(go.Bar(
            y=df_sorted.index, x=df_sorted['1Y %'], 
            name='1 Year', orientation='h', marker_color='#4c8c2b'
        ))

        # YTD Bar (Blue/Cyan)
        fig.add_trace(go.Bar(
            y=df_sorted.index, x=df_sorted['YTD %'], 
            name='YTD', orientation='h', marker_color='#17a2b8'
        ))
        
        fig.update_layout(
            title="JPX-Listed MSCI ETF Performance",
            xaxis_title="Return (%)",
            barmode='group',
            height=900,  # Adjusted height for full list
            template="plotly_white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        return fig

    # 5. Visualization: Valuation Table
    # ---------------------------------------------------------
    # Note: 'display()' is for Jupyter. We will just print the dataframe in standard script.
    
    # --- EXECUTION ---
    print("\nGenerating Dashboard...")
    fig = plot_msci_performance(df_final)
    fig.show()

    print("\n--- Valuation Table ---")
    cols = ['Ticker', 'Price (JPY)', 'YTD %', '1M %', '3M %', '1Y %', 'P/E', 'P/B', 'Yield %']
    # Filter columns that actually exist in the dataframe
    cols = [c for c in cols if c in df_final.columns]
    
    # Sort and print
    print(df_final[cols].sort_values('YTD %', ascending=False).to_markdown())

else:
    print("No data fetched. Please check your internet connection or ticker list.")
