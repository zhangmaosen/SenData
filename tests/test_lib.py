import os
from dotenv import load_dotenv
from src.lib.sen_stock import SenStock

# Load env vars
load_dotenv()

def test_sen_stock_yfinance():
    print("Testing SenStock with yfinance...")
    # Use a proxy if needed, environment variables should be set by load_dotenv or manually if testing proxy specifically
    # For this test, we assume the environment is set up correctly (including proxy if needed)
    
    stock = SenStock("AAPL", source="yfinance")
    
    print("  Fetching price history...")
    df = stock.get_price_history("2024-01-01", "2024-01-05")
    if not df.empty:
        print(f"  Success: {len(df)} rows fetched.")
    else:
        print("  Warning: Price history empty.")

    print("  Fetching company info...")
    info = stock.get_company_info()
    if info:
        print(f"  Success: Info fetched for {info.get('shortName', 'Unknown')}")
    else:
        print("  Warning: Company info empty.")

def test_sen_stock_alpha_vantage():
    print("\nTesting SenStock with Alpha Vantage...")
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    if not api_key:
        print("  Skipping: ALPHA_VANTAGE_API_KEY not found.")
        return

    stock = SenStock("AAPL", source="alpha_vantage", api_key=api_key)
    
    print("  Fetching news sentiment...")
    try:
        news = stock.get_news_sentiment()
        if not news.empty:
            print(f"  Success: {len(news)} news items fetched.")
        else:
            print("  Warning: News sentiment empty.")
    except Exception as e:
        print(f"  Error: {e}")

if __name__ == "__main__":
    # Set proxy for testing if needed, similar to main.py
    # os.environ['http_proxy'] = 'http://127.0.0.1:15236'
    # os.environ['https_proxy'] = 'http://127.0.0.1:15236'
    
    test_sen_stock_yfinance()
    test_sen_stock_alpha_vantage()
