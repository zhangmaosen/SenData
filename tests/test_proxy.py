import os
import yfinance as yf

# Set proxy
proxy = 'http://127.0.0.1:15236'
os.environ['http_proxy'] = proxy
os.environ['https_proxy'] = proxy

print(f"Testing yfinance with proxy: {proxy}")

try:
    symbol = "AAPL"
    print(f"Fetching info for {symbol}...")
    ticker = yf.Ticker(symbol)
    
    # Try fetching history as it's a common operation
    history = ticker.history(period="1d")
    
    if not history.empty:
        print("Success! Data fetched:")
        print(history)
    else:
        print("Data fetched but empty.")
        
except Exception as e:
    print(f"Error fetching data: {e}")
