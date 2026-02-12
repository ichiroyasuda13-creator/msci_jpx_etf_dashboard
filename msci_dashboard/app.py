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
MSCI_TICKERS = {meta["Index"]: ticker for ticker, meta in ETF_METADATA.items()}
CATEGORIES = {}
for ticker, meta in ETF_METADATA.items():
    cat = meta["Category"]
    if cat not in CATEGORIES:
        CATEGORIES[cat] = []
    CATEGORIES[cat].append(meta["Index"])

# --- DATA FETCHING ---

# --- DATA FETCHING ---

@st.cache_data(ttl=3600*12)
def fetch_data():
    """Fetches history with safety measures."""
    # 3 years + buffer (User Request)
    start_date = datetime.now() - timedelta(days=365*3 + 30)
    
    # Full list
    tickers_list = list(MSCI_TICKERS.values())
    
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

        # Rename
        ticker_to_index = {v: k for k, v in MSCI_TICKERS.items()}
        df_close.rename(columns=ticker_to_index, inplace=True)
        
        # Clean
        df_close.index = df_close.index.tz_localize(None)
        df_close.ffill(inplace=True) # Updated from method='ffill'
        
        return df_close
        
    except Exception as e:
        st.error(f"Fetch Error: {e}")
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
    """Calculates returns for all requested available timeframes."""
    results = {}
    
    if df_prices.empty:
        return pd.DataFrame()

    current_date = df_prices.index[-1]
    last_prices = df_prices.iloc[-1]
    
    # Helper to get price N days/months ago
    # We use 'asof' logic by looking for the index location
    def get_pct_change(days=None, hard_date=None):
        if hard_date:
            target_date = hard_date
        else:
            target_date = current_date - timedelta(days=days)
        
        # Find index of closest date on or before target
        # Use simple masking
        past_data = df_prices[df_prices.index <= target_date]
        if past_data.empty:
            return pd.Series([None]*len(df_prices.columns), index=df_prices.columns)
            
        start_prices = past_data.iloc[-1]
        return ((last_prices - start_prices) / start_prices) * 100

    # 1. Standard Periods
    results['1D'] = get_pct_change(days=1)
    results['1W'] = get_pct_change(days=7)
    results['1M'] = get_pct_change(days=30)
    results['3M'] = get_pct_change(days=91)
    results['1Yr'] = get_pct_change(days=365)
    results['3Yr'] = get_pct_change(days=365*3)
    results['5Yr'] = get_pct_change(days=365*5)
    # results['10Yr'] = get_pct_change(days=365*10) # Removed per user request

    # 2. Calendar Periods
    # MTD: End of last month
    mtd_target = current_date.replace(day=1) - timedelta(days=1)
    results['MTD'] = get_pct_change(hard_date=mtd_target)
    
    # QTD: End of last quarter
    # (Simplified: if we are in Feb, QTD is since Dec 31)
    curr_month = current_date.month
    q_month = ((curr_month - 1) // 3) * 3 + 1
    qtd_start = datetime(current_date.year, q_month, 1) - timedelta(days=1)
    results['QTD'] = get_pct_change(hard_date=qtd_start)
    
    # YTD: End of last year
    ytd_target = datetime(current_date.year - 1, 12, 31)
    results['YTD'] = get_pct_change(hard_date=ytd_target)

    return pd.DataFrame(results)

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
    valid_tickers = [t for t, m in ETF_METADATA.items() if m["Category"] in selected_categories]
    valid_indices = [ETF_METADATA[t]["Index"] for t in valid_tickers if t in ETF_METADATA]
    
    # Filter Dataframes
    if not df_prices.empty:
        # Keep only columns that are in valid_indices
        cols_to_keep = [c for c in df_prices.columns if c in valid_indices]
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
    df_sliced = filter_by_timeframe(df_prices, selected_tf)
    
    # Rebase to 0%
    if not df_sliced.empty:
        df_normalized = (df_sliced / df_sliced.iloc[0] - 1) * 100
    else:
        df_normalized = df_sliced

    # 3. Main Chart: Performance
    st.subheader("Performance")
    
    # User selection for highlight
    multiselect_container = st.container()
    all_options = list(df_normalized.columns)
    
    # Defaults (Adjust based on filter)
    # Only keep defaults if they are in the filtered list
    default_candidates = ["MSCI ACWI", "MSCI Japan High Div", "MSCI EM"]
    defaults = [x for x in default_candidates if x in all_options]
    
    # If no defaults remain (e.g. filtered out), pick the first one
    if not defaults and all_options:
        defaults = [all_options[0]]
    
    with multiselect_container:
        selected_indices = st.multiselect("Compare Indices:", all_options, default=defaults)

    if selected_indices:
        fig = go.Figure()
        for col in selected_indices:
            # Find matching metadata for tooltips
            ticker = MSCI_TICKERS.get(col, "")
            etf_name = ETF_METADATA.get(ticker, {}).get("Name", "")
            
            fig.add_trace(go.Scatter(
                x=df_normalized.index, 
                y=df_normalized[col], 
                mode='lines', 
                name=col,
                hovertemplate=f"<b>{col}</b><br>{etf_name}<br>%{{y:.2f}}%<extra></extra>"
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

    # 5. Detailed Table
    st.subheader("Performance and valuations (%)")
    
    # Base Data: Performance
    df_display = df_perf.copy()
    
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
        df_final = df_fund.merge(df_perf, left_on="Index Name", right_index=True, how="left")
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
        selected_etfs_price = st.multiselect("Select ETF/Index", df_prices.columns, default=[df_prices.columns[0]])
        
        col1, col2 = st.columns([4, 1])
        with col1:
            price_tf = st.radio("Chart Time Frame", time_frames, horizontal=True, index=len(time_frames)-1, key="price_chart_tf")
        with col2:
            normalize = st.checkbox("Normalize (%)", value=False)
        
        if selected_etfs_price:
            # Filter
            df_price_sliced = filter_by_timeframe(df_prices[selected_etfs_price], price_tf)
            
            if normalize and not df_price_sliced.empty:
                 df_price_sliced = (df_price_sliced / df_price_sliced.iloc[0] - 1) * 100
                 
            st.line_chart(df_price_sliced)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        import traceback
        st.error(f"An error occurred: {e}")
        st.code(traceback.format_exc())
