import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf
from datetime import datetime, timedelta

# --- CONFIGURATION & STYLING ---
st.set_page_config(page_title="MSCI ETF Dashboard", layout="wide", page_icon="📈")

# Custom CSS for "Premium" look
st.markdown("""
<style>
    /* Main container styling */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    /* Headers */
    h1, h2, h3 {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        color: #2c3e50;
    }
    /* Metric Cards */
    div[data-testid="stMetric"] {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        padding: 10px;
        border-radius: 5px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
    }
    .stTabs [aria-selected="true"] {
        background-color: #ffffff;
        border-bottom: 2px solid #e03131; /* Highlight color */
        color: #e03131;
    }
    /* Reduce font size for metric values to fit long Japanese names */
    div[data-testid="stMetricValue"] {
        font-size: 1.1rem !important;
        line-height: 1.4 !important;
        word-wrap: break-word;
        white-space: normal;
    }
</style>
""", unsafe_allow_html=True)

# --- DATA CONSTANTS ---
# Structure: Ticker: (Index Name, ETF Name, Category)
# Categories: 0=Global/Regional, 1=Japan Strategy
ETF_METADATA = {
    # 1. 日本株（テーマ別）
    "1477.T": {"Index": "MSCI 日本株最小分散指数(配当込み)", "Name": "iシェアーズ　MSCI 日本株最小分散 ETF", "Category": "日本株（テーマ別）"},
    "1478.T": {"Index": "MSCI ジャパン高配当利回り指数(配当込み)", "Name": "iシェアーズ　MSCI ジャパン高配当利回り ETF", "Category": "日本株（テーマ別）"},
    "1399.T": {"Index": "MSCIジャパンIMIカスタム高流動性高利回り低ボラティリティ指数", "Name": "上場インデックスファンドMSCI日本株高配当低ボラティリティ", "Category": "日本株（テーマ別）"},
    "1479.T": {"Index": "MSCI日本株人材設備投資指数(配当込み)", "Name": "iFreeETF MSCI日本株人材設備投資指数", "Category": "日本株（テーマ別）"},
    "1652.T": {"Index": "MSCI日本株女性活躍指数(配当込み)", "Name": "iFreeETF MSCI日本株女性活躍指数(WIN)", "Category": "日本株（テーマ別）"},
    "2518.T": {"Index": "MSCI 日本株女性活躍指数(セレクト) (配当込み)", "Name": "ＮＥＸＴ ＦＵＮＤＳ ＭＳＣＩ日本株女性活躍指数(セレクト)連動型上場投信", "Category": "日本株（テーマ別）"},
    "1653.T": {"Index": "MSCIジャパンESGセレクト・リーダーズ指数(配当込み)", "Name": "iFreeETF MSCIジャパンESGセレクト・リーダーズ指数", "Category": "日本株（テーマ別）"},
    "2564.T": {"Index": "MSCI ジャパン・高配当セレクト25指数(配当込み)", "Name": "グローバルＸ MSCIスーパーディビィデンド-日本株式 ETF", "Category": "日本株（テーマ別）"},
    "2636.T": {"Index": "MSCI Japan Governance-Quality Index (配当込み)", "Name": "グローバルＸ MSCI ガバナンス・クオリティ-日本株式 ETF", "Category": "日本株（テーマ別）"},
    "2643.T": {"Index": "MSCI ジャパンカントリー指数(セレクト) (配当込み)", "Name": "NEXT FUNDS MSCIジャパンカントリー指数(セレクト)連動型上場投信", "Category": "日本株（テーマ別）"},
    "2848.T": {"Index": "MSCI Japan Climate Change Index (配当込み)", "Name": "グローバルＸ MSCI 気候変動対応-日本株式 ETF", "Category": "日本株（テーマ別）"},
    "2851.T": {"Index": "MSCIジャパン 700 SRIセレクト指数(配当込み)", "Name": "iシェアーズ　MSCI ジャパンSRI ETF", "Category": "日本株（テーマ別）"},
    "2250.T": {"Index": "MSCIジャパン気候変動アクション指数(配当込み)", "Name": "iシェアーズ　MSCI ジャパン気候変動アクション ETF", "Category": "日本株（テーマ別）"},
    "234A.T": {"Index": "MSCI Japan IMI High Free Cash Flow Yield 50 Select Index (配当込み)", "Name": "グローバルＸ MSCI キャッシュフローキング-日本株式 ETF", "Category": "日本株（テーマ別）"},
    "294A.T": {"Index": "MSCIジャパン気候変動指数(セレクト) (配当込み)", "Name": "ＮＥＸＴ ＦＵＮＤＳ ＭＳＣＩジャパン気候変動指数(セレクト)連動型上場投信", "Category": "日本株（テーマ別）"},

    # 2. 外国株
    "1680.T": {"Index": "MSCI-KOKUSAIインデックス", "Name": "上場インデックスファンド海外先進国株式(MSCI-KOKUSAI)", "Category": "外国株"},
    "1550.T": {"Index": "MSCI-KOKUSAIインデックス", "Name": "MAXIS 海外株式(MSCIコクサイ)上場投信", "Category": "外国株"},
    "2513.T": {"Index": "MSCI-KOKUSAIインデックス", "Name": "ＮＥＸＴ ＦＵＮＤＳ 外国株式・ＭＳＣＩ‐ＫＯＫＵＳＡＩ指数(為替ヘッジなし)連動型上場投信", "Category": "外国株"},
    "2514.T": {"Index": "MSCI-KOKUSAI指数(円ペース・為替ヘッジあり)", "Name": "ＮＥＸＴ ＦＵＮＤＳ 外国株式・ＭＳＣＩ‐ＫＯＫＵＳＡＩ指数(為替ヘッジあり)連動型上場投信", "Category": "外国株"},
    "1681.T": {"Index": "MSCI エマージング・マーケット・インデックス", "Name": "上場インデックスファンド海外新興国株式(MSCIエマージング)", "Category": "外国株"},
    "2520.T": {"Index": "MSCI エマージング・マーケット・インデックス", "Name": "ＮＥＸＴ ＦＵＮＤＳ新興国株式・MSCIエマージング・マーケット・インデックス(為替ヘッジなし)連動型上場投信", "Category": "外国株"},
    "1554.T": {"Index": "MSCI ACWI ex Japanインデックス", "Name": "上場インデックスファンド世界株式(MSCI ACWI)除く日本", "Category": "外国株"},
    "2559.T": {"Index": "MSCI ACWIインデックス", "Name": "ＭＡＸＩＳ全世界株式(オール・カントリー)上場投信", "Category": "外国株"},
    "1657.T": {"Index": "MSCI コクサイ指数(税引後配当込み、国内投信用、円建て)", "Name": "iシェアーズ・コア MSCI 先進国株(除く日本)ETF", "Category": "外国株"},
    "1658.T": {"Index": "MSCI エマージング・マーケッツ IMI 指数(税引後配当込み、国内投信用、円建て)", "Name": "iシェアーズ・コア MSCI 新興国株 ETF", "Category": "外国株"},
    "273A.T": {"Index": "ＭＳＣＩ　サウジアラビア・インデックス(円換算ベース)", "Name": "ＳＢＩ サウジアラビア株式上場投信", "Category": "外国株"},

    # 3. エンハンスト型
    "1490.T": {"Index": "MSCIジャパンIMIカスタムロングショート戦略85%+円キャッシュ15%指数", "Name": "上場インデックスファンドMSCI日本株高配当低ボラティリティ(βヘッジ)", "Category": "エンハンスト型"},
}

# Invert for data fetching logic
# PROBLEM: Index Names are NOT unique. We must use a list of tickers or map Ticker -> Index.
# We already have ETF_METADATA which is Ticker -> Meta.
# Let's just use ETF_METADATA.keys() for fetching.

MSCI_TICKERS_LIST = list(ETF_METADATA.keys())

# CATEGORIES mapping (Category -> [Tickers])
CATEGORIES = {}
for ticker, meta in ETF_METADATA.items():
    cat = meta["Category"]
    if cat not in CATEGORIES:
        CATEGORIES[cat] = []
    CATEGORIES[cat].append(ticker) # Store Ticker, not Index Name

# --- DATA FETCHING ---

@st.cache_data(ttl=3600*12)
def fetch_data():
    """Fetches history with safety measures."""
    # 3 years + buffer (User Request)
    start_date = datetime.now() - timedelta(days=365*3 + 30)
    
    tickers_list = MSCI_TICKERS_LIST
    
    try:
        # optimize: Download in batches to avoid Timeouts/Memory issues on Cloud
        chunk_size = 5
        dfs = []
        
        # Progress bar
        progress_bar = st.progress(0)
        
        for i in range(0, len(tickers_list), chunk_size):
            batch = tickers_list[i:i + chunk_size]
            try:
                # Download batch
                df_batch = yf.download(batch, start=start_date, progress=False, threads=False) # threads=False is surprisingly safer for small batches on cloud
                
                if not df_batch.empty:
                    # Isolate Close column for this batch
                    if isinstance(df_batch.columns, pd.MultiIndex):
                        # yfinance structure: (Price, Ticker)
                        # We want Close price for each ticker
                        if 'Close' in df_batch.columns.get_level_values(0):
                             dfs.append(df_batch['Close'])
                        else:
                             dfs.append(df_batch.xs('Close', axis=1, level=1, drop_level=True))
                    else:
                        if 'Close' in df_batch.columns:
                             dfs.append(df_batch['Close'])
                        else:
                             dfs.append(df_batch)
            except Exception as e:
                print(f"Error fetching batch {batch}: {e}")
            
            # Update progress
            progress_bar.progress(min((i + chunk_size) / len(tickers_list), 1.0))
            
        progress_bar.empty()
        
        if not dfs:
            st.error("Download returned empty dataframe.")
            return pd.DataFrame()

        # Combine batches
        df_close = pd.concat(dfs, axis=1)

        # Clean
        df_close.index = df_close.index.tz_localize(None)
        df_close.ffill(inplace=True)
        
        # Ensure columns are Tickers (yfinance usually does this, but let's be sure)
        # If we had single ticker batch, it might not have ticker name as column
        # Batch download normally returns dataframe with columns = Tickers
        
        return df_close
        
    except Exception as e:
        st.error(f"Fetch Error: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=300) # shorter cache for intraday
def fetch_intraday_data(tickers):
    """Fetches 1D intraday data (5m interval) for selected tickers."""
    if not tickers:
        return pd.DataFrame()
        
    try:
        # Download in one go (small enough usually) or batch if needed
        # For 1D intraday, yfinance is usually fast.
        df    = yf.download(tickers, period="1d", interval="5m", progress=False, threads=True)
        
        if df.empty:
            return pd.DataFrame()
            
        # Extract Close
        if isinstance(df.columns, pd.MultiIndex):
            if 'Close' in df.columns.get_level_values(0):
                 df_close = df['Close']
            else:
                 df_close = df.xs('Close', axis=1, level=1, drop_level=True)
        else:
            if 'Close' in df.columns:
                 df_close = df['Close']
            else:
                 df_close = df
                 
        # No Rename needed - we want Tickers as columns
        # ticker_to_index = {v: k for k, v in MSCI_TICKERS.items() if v in tickers}
        # df_close.rename(columns=ticker_to_index, inplace=True)
        
        # Clean
        df_close.index = df_close.index.tz_localize(None)
        df_close.ffill(inplace=True)
        
        return df_close
    except Exception as e:
        st.error(f"Intraday Fetch Error: {e}")
        return pd.DataFrame()

@st.cache_data
def get_fundamentals():
    """Fetches fundamental data (Snapshot fallback for Cloud)."""
    rows = []
    
    # 1. Try Loading Snapshot (Fastest/Safest for Cloud)
    import json
    import os
    
    # Locate json in the same directory as app.py
    snapshot_path = os.path.join(os.path.dirname(__file__), 'etf_snapshot.json')
    if os.path.exists(snapshot_path):
        try:
            with open(snapshot_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                df = pd.DataFrame(data)
                # Ensure Metadata Columns exist (Critical for Merge)
                df["Index Name"] = df["Ticker"].map(lambda t: ETF_METADATA.get(t, {}).get("Index", ""))
                df["ETF Name"] = df["Ticker"].map(lambda t: ETF_METADATA.get(t, {}).get("Name", ""))
                return df.set_index("Ticker", drop=False)
        except:
            pass
            
    # 2. Live Fetch (Fallback/Local)
    # On Streamlit Cloud, this often returns empty or blocks.
    for ticker, meta in ETF_METADATA.items():
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            price = info.get('regularMarketPreviousClose') or info.get('previousClose')
            nav = info.get('navPrice')
            
            premium = None
            if price and nav:
                premium = ((price - nav) / nav) * 100
            
            rows.append({
                "Index Name": meta["Index"],
                "ETF Name": meta["Name"], 
                "Ticker": ticker,
                "Price": price,
                "NAV": nav,
                "Premium %": premium,
                "AUM (B)": info.get('totalAssets'),
                "P/E": info.get('trailingPE'),
                "P/B": info.get('priceToBook'),
                "Yield %": (info.get('yield', 0) or 0) * 100
            })
        except:
            pass
    return pd.DataFrame(rows)

def calculate_returns(df_prices):
    """Calculates returns for all requested available timeframes, handling data gaps robustly."""
    results = {}
    
    if df_prices.empty:
        return pd.DataFrame()

    # We need to process each column individually because tickers might have different end dates
    # (e.g. Foreign ETFs vs Japan ETFs with different holidays)
    
    periods = {
        '1D': 1,
        '1W': 7,
        '1M': 30,
        '3M': 91,
        '1Yr': 365,
        '3Yr': 365*3,
        '5Yr': 365*5
    }
    
    # Pre-calculate calendar dates (base reference is today)
    now = datetime.now()
    # For calendar metrics (YTD, MTD), we still use a fixed reference point relative to the LATEST data available.
    # But ideally, we should use the latest date *per ticker*.
    
    final_data = []

    for ticker in df_prices.columns:
        series = df_prices[ticker].dropna()
        if series.empty:
            continue
            
        last_dt = series.index[-1]
        last_price = series.iloc[-1]
        
        ticker_res = {}
        ticker_res['Ticker'] = ticker # temporary key for alignment
        
        # 1. Rolling Periods
        for name, days in periods.items():
            target_dt = last_dt - timedelta(days=days)
            # Find price on or before target
            past_series = series[series.index <= target_dt]
            if not past_series.empty:
                start_price = past_series.iloc[-1]
                ticker_res[name] = ((last_price - start_price) / start_price) * 100
            else:
                ticker_res[name] = None
        
        # 2. Calendar Periods
        # MTD
        mtd_target = last_dt.replace(day=1) - timedelta(days=1)
        past_series = series[series.index <= mtd_target]
        if not past_series.empty:
             ticker_res['MTD'] = ((last_price - past_series.iloc[-1]) / past_series.iloc[-1]) * 100
        else:
             ticker_res['MTD'] = None

        # QTD
        curr_month = last_dt.month
        q_month = ((curr_month - 1) // 3) * 3 + 1
        qtd_target = datetime(last_dt.year, q_month, 1) - timedelta(days=1)
        past_series = series[series.index <= qtd_target]
        if not past_series.empty:
             ticker_res['QTD'] = ((last_price - past_series.iloc[-1]) / past_series.iloc[-1]) * 100
        else:
             ticker_res['QTD'] = None

        # YTD
        ytd_target = datetime(last_dt.year - 1, 12, 31)
        past_series = series[series.index <= ytd_target]
        if not past_series.empty:
             ticker_res['YTD'] = ((last_price - past_series.iloc[-1]) / past_series.iloc[-1]) * 100
        else:
             ticker_res['YTD'] = None
             
        final_data.append(ticker_res)
        
    if not final_data:
        return pd.DataFrame()
        
    # Convert to DataFrame
    df_res = pd.DataFrame(final_data)
    if 'Ticker' in df_res.columns:
        # Match index to original df_prices columns (Tickers/Index Names)
        # But wait, df_prices columns ARE the names (Index Names or Tickers depending on where this is called).
        # In main, we renamed columns to 'Index Name'.
        # Let's verify what df_prices.columns are.
        # In fetch_data, we did: ticker_to_index = ... rename ...
        # So columns are "MSCI ACWI", etc.
        
        # We need to set the index back to the column name
        df_res.set_index('Ticker', inplace=True)
    
    return df_res

def filter_by_timeframe(df, timeframe):
    """Filters dataframe based on selected timeframe."""
    if df.empty:
        return df
        
    end_date = df.index[-1]
    start_date = df.index[0] # Default filter
    
    if timeframe == "1D":
        start_date = end_date - timedelta(days=1)
    elif timeframe == "1W":
        start_date = end_date - timedelta(days=7)
    elif timeframe == "1M":
        start_date = end_date - timedelta(days=30)
    elif timeframe == "3M":
        start_date = end_date - timedelta(days=90)
    elif timeframe == "1Yr":
        start_date = end_date - timedelta(days=365)
    elif timeframe == "3Yr":
        start_date = end_date - timedelta(days=365*3)
    elif timeframe == "YTD":
        start_date = datetime(end_date.year, 1, 1)
    elif timeframe == "MTD":
        start_date = datetime(end_date.year, end_date.month, 1) 
    elif timeframe == "QTD":
        q_month = ((end_date.month - 1) // 3) * 3 + 1
        start_date = datetime(end_date.year, q_month, 1)
    elif timeframe == "MAX":
        start_date = df.index[0]
        
    return df[df.index >= start_date].copy()

# --- CONFIGURATION & STYLING ---
st.set_page_config(page_title="MSCI ETF Dashboard Ver.1", layout="wide", page_icon="📈")

# --- APP LOGIC ---

def main():
    # DEBUG CHECKPOINT
    # st.write("Initializing Dashboard...")
    
    st.title("MSCI ETF Dashboard Ver.2")
    
    # Verification Timestamp (moved later)

    st.caption("Tracking JPX-Listed MSCI ETFs")

    # ... (skipping lines) ...
    


    # ... (formatting) ...

    # 1. Fetch Data
    status_text = st.empty()
    status_text.text("Fetching 3 years of data... please wait.")
    
    df_prices = fetch_data()
    df_fund = get_fundamentals()
    
    status_text.empty()

    # --- CATEGORY FILTER ---
    st.sidebar.header("Filter Options")
    
    # Get unique categories
    all_categories = sorted(list(set(m["Category"] for m in ETF_METADATA.values())))
    
    # Sidebar Multiselect
    selected_categories = st.sidebar.multiselect(
        "Select Category",
        options=all_categories,
        default=all_categories
    )
    
    # Filter Tickers based on Category
    
    # Filter Tickers based on Category
    valid_tickers = [t for t, m in ETF_METADATA.items() if m["Category"] in selected_categories]
    # valid_indices is no longer needed for filtering df_prices, as df_prices now uses Tickers
    
    # Filter Dataframes
    if not df_prices.empty:
        # Keep only columns that are in valid_tickers
        cols_to_keep = [c for c in df_prices.columns if c in valid_tickers]
        df_prices = df_prices[cols_to_keep]

    if not df_fund.empty:
        # Filter fundamental rows
        df_fund = df_fund[df_fund["Ticker"].isin(valid_tickers)]

    # Verification Timestamp (Placed here to ensure df_prices is defined)
    if not df_prices.empty:
        last_dt = df_prices.index[-1]
        st.caption(f"Data as of: {last_dt.strftime('%Y-%m-%d')}")
    else:
        st.caption("Data as of: Unknown")

    if df_prices.empty:
        st.error("No data available. Please check connections or adjust filters.")
        return

    # 2. Time Frame Selection
    # 1D, 1W, 1M, 3M, MTD, QTD, YTD, 1Yr, 3Yr
    time_frames = [
        "1D", "1W", "1M", "3M", "MTD", "QTD", "YTD", "1Yr", "3Yr", "MAX"
    ]
    
    col_opt, col_blank = st.columns([4, 1]) # Adjust width
    with col_opt:
        selected_tf = st.radio("Time Frame", time_frames, horizontal=True, label_visibility="collapsed")

    # Filter Data based on Time Frame
    if selected_tf == "1D":
        # Special Case: Fetch Intraday
        intraday_tickers = valid_tickers
        with st.spinner("Fetching intraday data..."):
             df_intraday = fetch_intraday_data(intraday_tickers)
        
        if not df_intraday.empty:
            df_sliced = df_intraday
        else:
             # Fallback
             df_sliced = filter_by_timeframe(df_prices, selected_tf)
    else:
        df_sliced = filter_by_timeframe(df_prices, selected_tf)
    
    # Rebase to 0%
    if not df_sliced.empty:
        # Use bfill to get the first VALID price for each ticker, even if they start at slightly different times.
        # This prevents the whole column from becoming NaN if iloc[0] is NaN.
        first_valid_prices = df_sliced.bfill().iloc[0]
        df_normalized = (df_sliced / first_valid_prices - 1) * 100
    else:
        df_normalized = df_sliced

    # 3. Main Chart: Performance
    st.subheader("Performance")
    
    # User selection for highlight
    multiselect_container = st.container()
    all_tickers = list(df_normalized.columns)
    
    # Helper to get display name for ticker (Performance Chart -> Index Name)
    def get_display_name(ticker):
        meta = ETF_METADATA.get(ticker, {})
        # User requested Index Name back for Performance Chart
        return f"{meta.get('Index', ticker)} ({ticker})"
        
    # Helper for Price Chart -> ETF Name
    def get_etf_display_name(ticker):
        meta = ETF_METADATA.get(ticker, {})
        etf_name = meta.get('Name', ticker)
        return f"{etf_name} ({ticker})"

    # Create mapping for multiselect
    # Ticker -> Display Name
    # But multiselect returns values. 
    # Let's simple use Tickers as options but format them? 
    # OR use Display Names and map back.
    # Simpler: Use Tickers as keys, format_func for display
    
    # Defaults (Adjust based on filter)
    # default_candidates = ["MSCI ACWI", "MSCI Japan High Div", "MSCI EM"] # These are Index Names.
    # We need Tickers now.
    default_candidates_tickers = ["2559.T", "1478.T", "1681.T"] # Update to Tickers
    
    defaults = [x for x in default_candidates_tickers if x in all_tickers]
    
    if not defaults and all_tickers:
        defaults = [all_tickers[0]]
    
    with multiselect_container:
        selected_tickers_chart = st.multiselect(
            "Compare Indices:", # Reverted Label
            all_tickers, 
            default=defaults,
            format_func=get_display_name
        )

    if selected_tickers_chart:
        fig = go.Figure()
        for col in selected_tickers_chart:
            # col is Ticker
            ticker = col
            meta = ETF_METADATA.get(ticker, {})
            index_name = meta.get("Index", "")
            etf_name = meta.get("Name", "")
            
            # Use Index Name for Legend to keep it clean
            legend_name = index_name if index_name else ticker

            fig.add_trace(go.Scatter(
                x=df_normalized.index, 
                y=df_normalized[col], 
                mode='lines', 
                name=legend_name,
                hovertemplate=f"<b>{legend_name}</b><br>{etf_name} ({ticker})<br>%{{y:.2f}}%<extra></extra>"
            ))
        
        fig.update_layout(
            hovermode="x unified",
            margin=dict(l=0, r=0, t=10, b=0),
            height=400,
            yaxis_title="Return (%)",
            template="plotly_white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)


    # Calculate All Returns (using full history for table correctness)
    df_perf = calculate_returns(df_prices)
    # df_perf index is now Tickers (from my previous fix + fetch_data fix)

    # 5. Detailed Table
    st.subheader("Performance and valuations (%)")
    
    # Base Data: Performance
    
    cols_perf = ['1D', '1W', '1M', '3M', 'MTD', 'QTD', 'YTD', '1Yr', '3Yr']
    cols_nav = ['Price', 'NAV', 'Premium %', 'AUM (B)']
    cols_fund = ['P/B', 'P/E', 'Yield %']
    cols_meta = ['Category', 'Index Name', 'ETF Name', 'Ticker']
    final_cols_order = cols_meta + cols_perf + cols_nav + cols_fund 

    if not df_fund.empty:
        # DEBUG: Check columns
        # st.write("Fund Columns:", df_fund.columns.tolist())
        # st.write("Perf Index:", df_perf.index.name)
        
        # Add Category if missing (from snapshot or live)
        if "Category" not in df_fund.columns:
             df_fund["Category"] = df_fund["Ticker"].map(lambda t: ETF_METADATA.get(t, {}).get("Category", ""))

        # Merge Performance with Fundamentals
        # df_fund has "Ticker" column. df_perf index is Ticker.
        # df_fund ALSO has Ticker as Index (from get_fundamentals).
        # We merge on Index to avoid "Ticker is both index and column" error.
        df_final = df_fund.merge(df_perf, left_index=True, right_index=True, how="left")
    else:
        st.warning("⚠️ Live fundamental data (NAV, P/E, AUM) temporarily unavailable. Showing Performance only.")
        df_final = df_perf.copy()
        df_final["Ticker"] = df_final.index
        df_final["Index Name"] = df_final.index.map(lambda t: ETF_METADATA.get(t, {}).get("Index", ""))
        df_final["ETF Name"] = df_final.index.map(lambda t: ETF_METADATA.get(t, {}).get("Name", ""))
        df_final["Category"] = df_final.index.map(lambda t: ETF_METADATA.get(t, {}).get("Category", ""))
        
        for c in cols_nav + cols_fund:
             df_final[c] = pd.NA
 
    # Filter only existing columns
    final_cols = [c for c in final_cols_order if c in df_final.columns]
    
    # Safe formatter
    def safe_fmt(fmt):
        return lambda x: fmt.format(x) if pd.notnull(x) and x is not None and x is not pd.NA else ""
        
    def fmt_aum(x):
        if pd.notnull(x) and x is not None and x is not pd.NA:
            try:
                return f"{float(x)/1_000_000_000:,.1f}B" # Billions
            except:
                return ""
        return ""

    format_dict = {c: safe_fmt("{:+.1f}") for c in cols_perf}
    format_dict.update({
        'Price': safe_fmt("{:,.0f}"),
        'NAV': safe_fmt("{:,.0f}"),
        'Premium %': safe_fmt("{:+.2f}"),
        'AUM (B)': fmt_aum,
        'P/B': safe_fmt("{:.1f}"),
        'P/E': safe_fmt("{:.1f}"),
        'Yield %': safe_fmt("{:.1f}"),
        'ETF Name': lambda x: x # String
    })

    st.dataframe(
        df_final[final_cols].style
        .format(format_dict)
        .background_gradient(subset=['YTD'], cmap="ocean_r", vmin=-20, vmax=40) 
        .set_properties(**{'white-space': 'wrap'}, subset=['Index Name', 'ETF Name']),
        use_container_width=True,
        height=800,
        hide_index=True
    )

    # 3. Chart (Optional, kept at bottom)
    with st.expander("Show Price Chart"):
        # Select ETF
        selected_etfs_price = st.multiselect("Select ETF/Index", df_prices.columns, default=[df_prices.columns[0]], format_func=get_etf_display_name)
        
        col1, col2 = st.columns([4, 1])
        with col1:
            price_tf = st.radio("Chart Time Frame", time_frames, horizontal=True, index=len(time_frames)-1, key="price_chart_tf")
        with col2:
            normalize = st.checkbox("Normalize (%)", value=False)
        
        if selected_etfs_price:
            # Filter
            if price_tf == "1D":
                 with st.spinner("Fetching intraday..."):
                     df_intraday = fetch_intraday_data(selected_etfs_price)
                 if not df_intraday.empty:
                     df_price_sliced = df_intraday
                 else:
                     df_price_sliced = filter_by_timeframe(df_prices[selected_etfs_price], price_tf)
            else:
                 df_price_sliced = filter_by_timeframe(df_prices[selected_etfs_price], price_tf)
            
            if normalize and not df_price_sliced.empty:
                 # Use bfill().iloc[0] for robustness against start-of-day NaNs
                 first_valid = df_price_sliced.bfill().iloc[0]
                 df_price_sliced = (df_price_sliced / first_valid - 1) * 100
            
            # Rename columns to ETF Name for Legend
            if not df_price_sliced.empty:
                # Create renaming dict: Ticker -> ETF Name
                rename_dict = {}
                for col in df_price_sliced.columns:
                     meta = ETF_METADATA.get(col, {})
                     name = meta.get('Name', col)
                     rename_dict[col] = f"{name} ({col})"
                
                df_chart = df_price_sliced.rename(columns=rename_dict)
                st.line_chart(df_chart)
            else:
                st.info("No data available for selected range.")


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        import traceback
        st.error(f"An error occurred: {e}")
        st.code(traceback.format_exc())
