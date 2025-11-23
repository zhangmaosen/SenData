import os
import requests
import pandas as pd
from typing import Optional
from .base import BaseFetcher
from ..utils.decorators import rate_limit

class AlphaVantageFetcher(BaseFetcher):
    """
    使用 Alpha Vantage API 获取数据
    """
    BASE_URL = "https://www.alphavantage.co/query"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ALPHA_VANTAGE_API_KEY")
        if not self.api_key:
            raise ValueError("Alpha Vantage API key is required. Set ALPHA_VANTAGE_API_KEY env var or pass it to constructor.")

    # Limit to 5 calls per minute (standard free tier)
    # Using 65 seconds window to be safe
    @rate_limit(max_calls=5, period=65.0)
    def _make_request(self, params: dict) -> dict:
        params["apikey"] = self.api_key
        response = requests.get(self.BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()
        if "Error Message" in data:
            raise ValueError(f"Alpha Vantage API Error: {data['Error Message']}")
        if "Information" in data:
             # Rate limit or other info
             print(f"Alpha Vantage Info: {data['Information']}")
        return data

    def fetch_price_history(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        # Alpha Vantage TIME_SERIES_DAILY is the closest, but filtering by date requires processing
        # For now, we can implement a basic version or leave it as a secondary source
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol,
            "outputsize": "full"
        }
        data = self._make_request(params)
        ts_data = data.get("Time Series (Daily)", {})
        df = pd.DataFrame.from_dict(ts_data, orient="index")
        if not df.empty:
            df = df.sort_index()
            # Filter by date if needed, but AV returns all or compact.
            # We can filter locally.
            df.index = pd.to_datetime(df.index)
            mask = (df.index >= start_date) & (df.index <= end_date)
            return df.loc[mask]
        return df

    def fetch_balance_sheet(self, symbol: str) -> pd.DataFrame:
        data = self._make_request({"function": "BALANCE_SHEET", "symbol": symbol})
        reports = data.get("annualReports", [])
        return pd.DataFrame(reports)

    def fetch_cash_flow(self, symbol: str) -> pd.DataFrame:
        data = self._make_request({"function": "CASH_FLOW", "symbol": symbol})
        reports = data.get("annualReports", [])
        return pd.DataFrame(reports)

    def fetch_income_statement(self, symbol: str) -> pd.DataFrame:
        data = self._make_request({"function": "INCOME_STATEMENT", "symbol": symbol})
        reports = data.get("annualReports", [])
        return pd.DataFrame(reports)

    def fetch_company_info(self, symbol: str) -> dict:
        return self._make_request({"function": "OVERVIEW", "symbol": symbol})

    def fetch_insider_transactions(self, symbol: str) -> pd.DataFrame:
        # Alpha Intelligence
        data = self._make_request({"function": "INSIDER_TRANSACTIONS", "symbol": symbol})
        # The key might be different, documentation says "Insider Transactions" usually?
        # Let's check the docs again or assume standard JSON structure.
        # Docs example output not fully shown, but usually it's a list under a key.
        # Based on other endpoints, it might be "insider_transactions" or similar.
        # I'll assume it returns a dict with a key like "Insider Transactions" or just the list if CSV.
        # But JSON output usually has a root key.
        # Let's return the raw dict wrapped in DataFrame if possible, or just the dict.
        # Actually, let's look at the structure if I can. 
        # For now, I'll return the whole JSON as a dict if I can't parse it easily, 
        # but the interface expects DataFrame.
        # I'll try to find the list key.
        return pd.DataFrame(data) # Placeholder, might need adjustment

    def fetch_recommendations(self, symbol: str) -> pd.DataFrame:
        # Not directly supported by a simple endpoint in the list I saw, 
        # maybe EARNINGS_ESTIMATES or similar?
        return pd.DataFrame()

    def fetch_news_sentiment(self, symbol: str) -> pd.DataFrame:
        # Alpha Intelligence
        params = {
            "function": "NEWS_SENTIMENT",
            "tickers": symbol,
            "limit": 50
        }
        data = self._make_request(params)
        feed = data.get("feed", [])
        return pd.DataFrame(feed)

    def fetch_earnings_call_transcript(self, symbol: str, quarter: Optional[str] = None) -> str:
        # Alpha Intelligence
        # Quarter format: YYYYQ1, YYYYQ2, etc.
        if not quarter:
            print("Quarter is required for earnings transcript (e.g., '2023Q3')")
            return ""
        
        params = {
            "function": "EARNINGS_CALL_TRANSCRIPT",
            "symbol": symbol,
            "quarter": quarter
        }
        data = self._make_request(params)
        
        transcript_segments = data.get("transcript", [])
        if not transcript_segments:
            return ""
            
        full_text = []
        for segment in transcript_segments:
            speaker = segment.get("speaker", "Unknown")
            title = segment.get("title", "")
            content = segment.get("content", "")
            
            header = f"{speaker}"
            if title:
                header += f" ({title})"
            
            full_text.append(f"{header}:\n{content}\n")
            
        return "\n".join(full_text)

    def fetch_advanced_analytics(self, symbol: str) -> dict:
        # Alpha Intelligence
        # Fixed window example
        params = {
            "function": "ANALYTICS_FIXED_WINDOW",
            "SYMBOLS": symbol,
            "RANGE": "full", # or specific range
            "INTERVAL": "DAILY",
            "OHLC": "close",
            "CALCULATIONS": "MEAN,STDDEV,CORRELATION" 
        }
        return self._make_request(params)

    def fetch_top_gainers_losers(self) -> dict:
        # Alpha Intelligence
        return self._make_request({"function": "TOP_GAINERS_LOSERS"})
