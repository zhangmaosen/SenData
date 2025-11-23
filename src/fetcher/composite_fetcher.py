import pandas as pd
from typing import Optional, List, Any
from .base import BaseFetcher
from .yfinance_fetcher import YFinanceFetcher
from .alpha_vantage_fetcher import AlphaVantageFetcher
from .local_fetcher import LocalFetcher
import os

class CompositeFetcher(BaseFetcher):
    """
    组合获取器，支持多数据源回退机制。
    默认优先使用 local -> yfinance -> alpha_vantage。
    """
    def __init__(self, api_key: Optional[str] = None, priority: Optional[List[str]] = None):
        self.local = LocalFetcher()
        self.yf = YFinanceFetcher()
        # Alpha Vantage requires API key, might be None if not provided/env var set
        try:
            self.av = AlphaVantageFetcher(api_key=api_key)
        except ValueError:
            self.av = None

        self.fetchers = []
        
        # Default priority: local -> yfinance -> alpha_vantage
        if priority:
            for p in priority:
                if p == "local":
                    self.fetchers.append(self.local)
                elif p == "yfinance":
                    self.fetchers.append(self.yf)
                elif p == "alpha_vantage" and self.av:
                    self.fetchers.append(self.av)
        else:
            # Default order
            self.fetchers.append(self.local)
            self.fetchers.append(self.yf)
            if self.av:
                self.fetchers.append(self.av)

    def _run_with_fallback(self, method_name: str, *args, **kwargs) -> Any:
        last_error = None
        for fetcher in self.fetchers:
            try:
                if not hasattr(fetcher, method_name):
                    continue
                
                method = getattr(fetcher, method_name)
                result = method(*args, **kwargs)
                
                # Check for "empty" results to trigger fallback
                if isinstance(result, pd.DataFrame):
                    if not result.empty:
                        return result
                elif isinstance(result, (dict, list, str)):
                    if result:
                        return result
                elif result is not None:
                    return result
                    
            except Exception as e:
                last_error = e
                # print(f"Warning: {type(fetcher).__name__}.{method_name} failed: {e}")
                continue
        
        # If all failed, return empty/default appropriate for the type
        # or raise the last error if it was a crash.
        # To be safe, we return empty structures matching the expected return type of the method.
        # But since this is generic, we might need to know the return type.
        
        # Let's look at the specific methods.
        if last_error:
            # If we want to suppress errors and return empty, we need to know what empty is.
            # If we want to bubble up errors when ALL sources fail, we raise.
            raise last_error
            
        return None

    def fetch_price_history(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        res = self._run_with_fallback("fetch_price_history", symbol, start_date, end_date)
        return res if res is not None else pd.DataFrame()

    def fetch_balance_sheet(self, symbol: str) -> pd.DataFrame:
        res = self._run_with_fallback("fetch_balance_sheet", symbol)
        return res if res is not None else pd.DataFrame()

    def fetch_cash_flow(self, symbol: str) -> pd.DataFrame:
        res = self._run_with_fallback("fetch_cash_flow", symbol)
        return res if res is not None else pd.DataFrame()

    def fetch_income_statement(self, symbol: str) -> pd.DataFrame:
        res = self._run_with_fallback("fetch_income_statement", symbol)
        return res if res is not None else pd.DataFrame()

    def fetch_company_info(self, symbol: str) -> dict:
        res = self._run_with_fallback("fetch_company_info", symbol)
        return res if res is not None else {}

    def fetch_insider_transactions(self, symbol: str) -> pd.DataFrame:
        res = self._run_with_fallback("fetch_insider_transactions", symbol)
        return res if res is not None else pd.DataFrame()

    def fetch_recommendations(self, symbol: str) -> pd.DataFrame:
        res = self._run_with_fallback("fetch_recommendations", symbol)
        return res if res is not None else pd.DataFrame()

    def fetch_news_sentiment(self, symbol: str) -> pd.DataFrame:
        res = self._run_with_fallback("fetch_news_sentiment", symbol)
        return res if res is not None else pd.DataFrame()

    def fetch_earnings_call_transcript(self, symbol: str, quarter: Optional[str] = None) -> str:
        res = self._run_with_fallback("fetch_earnings_call_transcript", symbol, quarter)
        return res if res is not None else ""

    def fetch_advanced_analytics(self, symbol: str) -> dict:
        res = self._run_with_fallback("fetch_advanced_analytics", symbol)
        return res if res is not None else {}

    # Extra method not in BaseFetcher but used in main
    def fetch_top_gainers_losers(self) -> dict:
        res = self._run_with_fallback("fetch_top_gainers_losers")
        return res if res is not None else {}
