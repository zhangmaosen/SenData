import argparse
import sys
import os
from dotenv import load_dotenv
from src.fetcher.composite_fetcher import CompositeFetcher
from src.storage.saver import FileSaver
from datetime import datetime, timedelta
import time
import random

# Set proxy for yfinance/requests
# User specified proxy: 127.0.0.1:15236
# Adding http:// prefix is generally safer for requests library
os.environ['http_proxy'] = 'http://127.0.0.1:15236'
os.environ['https_proxy'] = 'http://127.0.0.1:15236'

# Load environment variables from .env file
load_dotenv()

def get_quarters_between(start_date_str, end_date_str):
    """Generate a list of quarters between start_date and end_date (inclusive)"""
    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
    except ValueError:
        # Fallback if dates are invalid or not provided correctly
        return get_recent_quarters(4)
    
    quarters = []
    
    # Start quarter
    current_year = start_date.year
    current_q = (start_date.month - 1) // 3 + 1
    
    # End quarter
    end_year = end_date.year
    end_q = (end_date.month - 1) // 3 + 1
    
    while (current_year < end_year) or (current_year == end_year and current_q <= end_q):
        quarters.append(f"{current_year}Q{current_q}")
        
        current_q += 1
        if current_q > 4:
            current_q = 1
            current_year += 1
            
    # Return in descending order (newest first) to match previous behavior
    return sorted(quarters, reverse=True)

def get_recent_quarters(n=4):
    """Generate a list of the last n quarters (e.g., ['2023Q4', '2023Q3', ...])"""
    quarters = []
    current_date = datetime.now()
    year = current_date.year
    month = current_date.month
    
    # Calculate current quarter
    current_q = (month - 1) // 3 + 1
    
    # Start from the previous quarter to ensure data availability
    # If we are in Q1, previous is Q4 of last year
    if current_q == 1:
        start_q = 4
        start_year = year - 1
    else:
        start_q = current_q - 1
        start_year = year
        
    q = start_q
    y = start_year
    
    for _ in range(n):
        quarters.append(f"{y}Q{q}")
        q -= 1
        if q == 0:
            q = 4
            y -= 1
            
    return quarters

def batch_download(symbols, start_date, end_date, source="yfinance", api_key=None, quarter=None, fetch_transcripts=False):
    # Initialize CompositeFetcher with priority based on source argument
    # If source is yfinance, priority is [yfinance, alpha_vantage]
    # If source is alpha_vantage, priority is [alpha_vantage, yfinance]
    priority = ["yfinance", "alpha_vantage"]
    if source == "alpha_vantage":
        priority = ["alpha_vantage", "yfinance"]
        
    fetcher = CompositeFetcher(api_key=api_key, priority=priority)
    saver = FileSaver(base_dir="data")

    # Market Movers (Alpha Vantage only, but CompositeFetcher handles it)
    if hasattr(fetcher, 'fetch_top_gainers_losers'):
        try:
            print("Fetching Top Gainers/Losers...")
            movers = fetcher.fetch_top_gainers_losers()
            if movers:
                saver.save_json("MARKET", "top_gainers_losers", movers)
        except Exception as e:
            print(f"Error fetching top gainers/losers: {e}")

    for symbol in symbols:
        print(f"Processing {symbol}...")
        
        # 1. Price History
        try:
            print(f"  Fetching price history...")
            price_df = fetcher.fetch_price_history(symbol, start_date, end_date)
            saver.save_dataframe(symbol, "price_history", price_df)
        except Exception as e:
            print(f"  Error fetching price history: {e}")

        # 2. Fundamentals
        try:
            print(f"  Fetching balance sheet...")
            bs = fetcher.fetch_balance_sheet(symbol)
            saver.save_dataframe(symbol, "balance_sheet", bs)
        except Exception as e:
            print(f"  Error fetching balance sheet: {e}")

        try:
            print(f"  Fetching cash flow...")
            cf = fetcher.fetch_cash_flow(symbol)
            saver.save_dataframe(symbol, "cash_flow", cf)
        except Exception as e:
            print(f"  Error fetching cash flow: {e}")

        try:
            print(f"  Fetching income statement...")
            income = fetcher.fetch_income_statement(symbol)
            saver.save_dataframe(symbol, "income_statement", income)
        except Exception as e:
            print(f"  Error fetching income statement: {e}")

        # 3. Company Info
        try:
            print(f"  Fetching company info...")
            info = fetcher.fetch_company_info(symbol)
            saver.save_json(symbol, "company_info", info)
        except Exception as e:
            print(f"  Error fetching company info: {e}")

        # 4. Insider Transactions
        try:
            print(f"  Fetching insider transactions...")
            insider = fetcher.fetch_insider_transactions(symbol)
            saver.save_dataframe(symbol, "insider_transactions", insider)
        except Exception as e:
            print(f"  Error fetching insider transactions: {e}")

        # 5. Recommendations
        try:
            print(f"  Fetching recommendations...")
            recs = fetcher.fetch_recommendations(symbol)
            saver.save_dataframe(symbol, "recommendations", recs)
        except Exception as e:
            print(f"  Error fetching recommendations: {e}")

        # 6. News & Sentiment
        try:
            print(f"  Fetching news & sentiment...")
            news = fetcher.fetch_news_sentiment(symbol)
            saver.save_dataframe(symbol, "news_sentiment", news)
        except Exception as e:
            print(f"  Error fetching news & sentiment: {e}")

        # 7. Earnings Call Transcript
        if quarter or fetch_transcripts:
            if quarter:
                quarters_to_fetch = [quarter]
            else:
                # Use the date range to determine quarters
                quarters_to_fetch = get_quarters_between(start_date, end_date)
                
            print(f"  Fetching earnings call transcripts for: {', '.join(quarters_to_fetch)}...")
            
            for q in quarters_to_fetch:
                try:
                    transcript = fetcher.fetch_earnings_call_transcript(symbol, q)
                    if transcript:
                        # Save as text file or JSON
                        saver.save_json(symbol, f"earnings_transcript_{q}", {"content": transcript})
                        print(f"    Saved transcript for {q}")
                    else:
                        print(f"    No transcript found for {q}")
                except Exception as e:
                    print(f"    Error fetching earnings transcript for {q}: {e}")

        # 8. Advanced Analytics
        try:
            print(f"  Fetching advanced analytics...")
            analytics = fetcher.fetch_advanced_analytics(symbol)
            saver.save_json(symbol, "advanced_analytics", analytics)
        except Exception as e:
            print(f"  Error fetching advanced analytics: {e}")

        print(f"Finished {symbol}.\n")

def main():
    parser = argparse.ArgumentParser(description="SenData Batch Collector")
    parser.add_argument("--symbols", nargs="+", help="List of stock symbols to download (e.g. AAPL MSFT)")
    parser.add_argument("--start", help="Start date (YYYY-MM-DD)", default=(datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d"))
    parser.add_argument("--end", help="End date (YYYY-MM-DD)", default=datetime.now().strftime("%Y-%m-%d"))
    parser.add_argument("--source", choices=["yfinance", "alpha_vantage"], default="yfinance", help="Data source")
    parser.add_argument("--api-key", help="API Key for Alpha Vantage")
    parser.add_argument("--quarter", help="Specific quarter for earnings transcript (e.g. 2023Q3)")
    parser.add_argument("--fetch-transcripts", action="store_true", help="Fetch recent earnings call transcripts (last 4 quarters)")
    
    args = parser.parse_args()

    if args.symbols:
        batch_download(args.symbols, args.start, args.end, args.source, args.api_key, args.quarter, args.fetch_transcripts)
    else:
        print("Please provide symbols using --symbols")
        parser.print_help()

if __name__ == "__main__":
    main()
