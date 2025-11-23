import os
import json
import pandas as pd
from typing import Optional
from .base import BaseFetcher

class LocalFetcher(BaseFetcher):
    """
    从本地文件系统获取数据。
    数据目录结构应符合 FileSaver 的保存格式：
    base_dir/
        SYMBOL/
            price_history.csv
            company_info.json
            ...
        MARKET/
            top_gainers_losers.json
    """
    def __init__(self, base_dir: str = "data"):
        self.base_dir = base_dir

    def _get_file_path(self, symbol: str, filename: str, ext: str) -> str:
        return os.path.join(self.base_dir, symbol, f"{filename}.{ext}")

    def _read_csv(self, symbol: str, filename: str) -> pd.DataFrame:
        path = self._get_file_path(symbol, filename, "csv")
        if os.path.exists(path):
            try:
                # Try to parse the first column as index (usually Date)
                df = pd.read_csv(path, index_col=0)
                # Try to convert index to datetime if it looks like a date
                try:
                    df.index = pd.to_datetime(df.index)
                except:
                    pass
                return df
            except Exception as e:
                print(f"Error reading local CSV {path}: {e}")
        return pd.DataFrame()

    def _read_json(self, symbol: str, filename: str) -> dict:
        path = self._get_file_path(symbol, filename, "json")
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error reading local JSON {path}: {e}")
        return {}

    def fetch_price_history(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        df = self._read_csv(symbol, "price_history")
        if not df.empty and isinstance(df.index, pd.DatetimeIndex):
            # Filter by date range
            mask = (df.index >= start_date) & (df.index <= end_date)
            return df.loc[mask]
        return df

    def fetch_balance_sheet(self, symbol: str) -> pd.DataFrame:
        return self._read_csv(symbol, "balance_sheet")

    def fetch_cash_flow(self, symbol: str) -> pd.DataFrame:
        return self._read_csv(symbol, "cash_flow")

    def fetch_income_statement(self, symbol: str) -> pd.DataFrame:
        return self._read_csv(symbol, "income_statement")

    def fetch_company_info(self, symbol: str) -> dict:
        return self._read_json(symbol, "company_info")

    def fetch_insider_transactions(self, symbol: str) -> pd.DataFrame:
        return self._read_csv(symbol, "insider_transactions")

    def fetch_recommendations(self, symbol: str) -> pd.DataFrame:
        return self._read_csv(symbol, "recommendations")

    def fetch_news_sentiment(self, symbol: str) -> pd.DataFrame:
        return self._read_csv(symbol, "news_sentiment")

    def fetch_earnings_call_transcript(self, symbol: str, quarter: Optional[str] = None) -> str:
        if not quarter:
            return ""
        filename = f"earnings_transcript_{quarter}"
        data = self._read_json(symbol, filename)
        return data.get("content", "")

    def fetch_advanced_analytics(self, symbol: str) -> dict:
        return self._read_json(symbol, "advanced_analytics")

    def fetch_top_gainers_losers(self) -> dict:
        # Market data is stored in MARKET folder
        path = os.path.join(self.base_dir, "MARKET", "top_gainers_losers.json")
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error reading local market data {path}: {e}")
        return {}
