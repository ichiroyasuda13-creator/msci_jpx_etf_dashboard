import yfinance as yf
import json
import pandas as pd
from datetime import datetime

# Define the list of tickers (from app.py)
ETF_METADATA = {
    # Global & Regional
    "2559.T": {"Index": "MSCI ACWI", "Name": "MAXIS全世界株式(オール・カントリー) 上場投信", "Category": "Global"},
    "1554.T": {"Index": "MSCI ACWI ex Japanインデックス", "Name": "上場インデックスファンド世界株式(MSCI ACWI)除く日本", "Category": "Global"},
    "1680.T": {"Index": "MSCI-KOKUSAIインデックス", "Name": "上場インデックスファンド海外先進国株式(MSCI-KOKUSAI)", "Category": "Dev Markets"},
    "1550.T": {"Index": "MSCI-KOKUSAIインデックス", "Name": "MAXIS 海外株式 (MSCIコクサイ)上場投信", "Category": "Dev Markets"},
    "2513.T": {"Index": "MSCI-KOKUSAIインデックス", "Name": "NEXT FUNDS外国株式・MSCI-KOKUSAI指数(為替ヘッジなし) 連動型上場投信", "Category": "Dev Markets"},
    "2514.T": {"Index": "MSCI-KOKUSAI指数(円ペース・為替ヘッジあり)", "Name": "NEXT FUNDS外国株式・MSCI-KOKUSAI指数(為替ヘッジあり)連動型上場投信", "Category": "Hedged/Specialty"},
    "1657.T": {"Index": "MSCI コクサイ指数(税引後配当込み、国内投信用、円建て)", "Name": "シェアーズ・コア MSCI 先進国株(除く日本)ETF", "Category": "Dev Markets"},
    
    # Emerging
    "1681.T": {"Index": "MSCI エマージング・マーケット・インデックス", "Name": "上場インデックスファンド海外新興国株式 (MSCIエマージング)", "Category": "Emerging"},
    "2520.T": {"Index": "MSCI エマージング・マーケット・インデックス", "Name": "NEXT FUNDS新興国株式・MSCIエマージング・マーケット・インデックス(為替ヘッジなし) 連動型上場投信", "Category": "Emerging"},
    "1658.T": {"Index": "MSCI エマージング・マーケッツ IMI指数(税引後配当込み、国内投信用、円建て)", "Name": "シェアーズ・コアMSCI 新興国株 ETF", "Category": "Emerging"},
    "273A.T": {"Index": "MSCI サウジアラビア・インデックス(円換算ベース)", "Name": "SBI サウジアラビア株式上場投信", "Category": "Emerging"},

    # Japan Strategy
    "1477.T": {"Index": "MSCI 日本株最小分散指数(配当込み)", "Name": "シェアーズ MSCI 日本株最小分散 ETF", "Category": "Japan Strategy"},
    "1478.T": {"Index": "MSCI ジャパン高配当利回り指数(配当込み)", "Name": "シェアーズ MSCI ジャパン高配当利回り ETF", "Category": "Japan Strategy"},
    "1399.T": {"Index": "MSCIジャパンIMIカスタム高流動性高利回り低ボラティリティ指数", "Name": "上場インデックスファンドMSCI日本株高配当低ボラティリティ", "Category": "Japan Strategy"},
    "1479.T": {"Index": "MSCI日本株人材設備投資指数(配当込み)", "Name": "iFreeETF MSCI日本株人材設備投資指数", "Category": "Japan Strategy"},
    "1652.T": {"Index": "MSCI日本株女性活躍指数(配当込み)", "Name": "iFreeETF MSCI日本株女性活躍指数(WIN)", "Category": "Japan Strategy"},
    "2518.T": {"Index": "MSCI 日本株女性活躍指数(セレクト) (配当込み)", "Name": "NEXT FUNDS MSCI日本株女性活躍指数(セレクト)連動型上場投信", "Category": "Japan Strategy"},
    "1653.T": {"Index": "MSCIジャパンESGセレクト・リーダーズ指数(配当込み)", "Name": "iFreeETF MSCIジャパンESGセレクト・リーダーズ指数", "Category": "Japan Strategy"},
    "2564.T": {"Index": "MSCI ジャパン・高配当セレクト25指数(配当込み)", "Name": "グローバルX MSCIスーパーディビィデンドー日本株式 ETF", "Category": "Japan Strategy"},
    "2636.T": {"Index": "MSCI Japan Governance-Quality Index (配当込み)", "Name": "グローバルX MSCI ガバナンス・クオリティー日本株式 ETF", "Category": "Japan Strategy"},
    "2643.T": {"Index": "MSCI ジャパンカントリー指数(セレクト) (配当込み)", "Name": "NEXT FUNDS MSCIジャパンカントリー指数(セレクト) 連動型上場投信", "Category": "Japan Strategy"},
    
    # Climate / SRI
    "2848.T": {"Index": "MSCI Japan Climate Change Index (配当込み)", "Name": "グローバルX MSCI 気候変動対応-日本株式ETF", "Category": "Climate/SRI"},
    "2851.T": {"Index": "MSCIジャパン 700 SRIセレクト指数(配当込み)", "Name": "シェアーズ MSCI ジャパンSRI ETF", "Category": "Climate/SRI"},
    "2250.T": {"Index": "MSCIジャパン気候変動アクション指数(配当込み)", "Name": "シェアーズ MSCI ジャパン気候変動アクション ETF", "Category": "Climate/SRI"},
    "294A.T": {"Index": "MSCIジャパン気候変動指数(セレクト) (配当込み)", "Name": "NEXT FUNDS MSCIジャパン気候変動指数(セレクト)連動型上場投信", "Category": "Climate/SRI"},
    
    # Other
    "234A.T": {"Index": "MSCI Japan IMI High Free Cash Flow Yield 50 Select Index (配当込み)", "Name": "グローバルX MSCI キャッシュフローキングー日本株式ETF", "Category": "Japan Strategy"},
    "1490.T": {"Index": "MSCIジャパンIMIカスタムロングショート戦略85%+円キャッシュ 15%指数", "Name": "上場インデックスファンドMSCI日本株高配当低ボラティリティ (Bヘッジ)", "Category": "Hedged/Specialty"},
}

def fetch_snapshot():
    print("Fetching fundamental data snapshot locally...")
    rows = []
    
    for ticker, meta in ETF_METADATA.items():
        print(f"Processing {ticker}...")
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Extract key metrics
            price = info.get('regularMarketPreviousClose') or info.get('previousClose')
            nav = info.get('navPrice')
            
            premium = None
            if price and nav:
                premium = ((price - nav) / nav) * 100
                
            data = {
                "Index Name": meta["Index"],
                "ETF Name": meta["Name"],
                "Ticker": ticker,
                "Price": price,
                "NAV": nav,
                "Premium %": premium,
                "AUM (B)": info.get('totalAssets'),
                "P/E": info.get('trailingPE'),
                "P/B": info.get('priceToBook'),
                "Yield %": (info.get('yield', 0) or 0) * 100,
                "Fetched At": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            rows.append(data)
        except Exception as e:
            print(f"Error fetching {ticker}: {e}")
            
    # Save to JSON
    with open("msci_dashboard/etf_snapshot.json", "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)
        
    print(f"Snapshot saved to msci_dashboard/etf_snapshot.json with {len(rows)} records.")

if __name__ == "__main__":
    fetch_snapshot()
