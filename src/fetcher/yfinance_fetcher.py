import yfinance as yf
import pandas as pd
import time
import random
from .base import BaseFetcher
from typing import Optional
from ..utils.decorators import random_delay

class YFinanceFetcher(BaseFetcher):
    """
    使用 yfinance 获取股票数据
    """

    @random_delay(2.0, 5.0)
    def fetch_price_history(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        ticker = yf.Ticker(symbol)
        # auto_adjust=True 会自动调整股价（类似 Adj Close），reference project 中也有用到
        df = ticker.history(start=start_date, end=end_date, auto_adjust=True)
        if df.empty:
            print(f"Warning: No price data found for {symbol}")
        return df

    @random_delay(2.0, 5.0)
    def fetch_balance_sheet(self, symbol: str) -> pd.DataFrame:
        ticker = yf.Ticker(symbol)
        # 默认获取年度，也可以扩展支持季度
        return ticker.balance_sheet

    @random_delay(2.0, 5.0)
    def fetch_cash_flow(self, symbol: str) -> pd.DataFrame:
        ticker = yf.Ticker(symbol)
        return ticker.cashflow

    @random_delay(2.0, 5.0)
    def fetch_income_statement(self, symbol: str) -> pd.DataFrame:
        ticker = yf.Ticker(symbol)
        return ticker.financials

    @random_delay(2.0, 5.0)
    def fetch_company_info(self, symbol: str) -> dict:
        ticker = yf.Ticker(symbol)
        return ticker.info

    @random_delay(2.0, 5.0)
    def fetch_insider_transactions(self, symbol: str) -> pd.DataFrame:
        ticker = yf.Ticker(symbol)
        return ticker.insider_transactions

    @random_delay(2.0, 5.0)
    def fetch_recommendations(self, symbol: str) -> pd.DataFrame:
        ticker = yf.Ticker(symbol)
        return ticker.recommendations

    @random_delay(2.0, 5.0)
    def fetch_news_sentiment(self, symbol: str) -> pd.DataFrame:
        ticker = yf.Ticker(symbol)
        news = ticker.news
        if news:
            return pd.DataFrame(news)
        return pd.DataFrame()

    def fetch_earnings_call_transcript(self, symbol: str, quarter: Optional[str] = None) -> str:
        # yfinance does not provide earnings call transcripts directly
        return ""

    def fetch_advanced_analytics(self, symbol: str) -> dict:
        # yfinance does not provide the specific "Advanced Analytics" like Alpha Vantage
        return {}
