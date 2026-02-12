import yfinance as yf
import json
import pandas as pd
from datetime import datetime

# Define the list of tickers (from app.py)
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
