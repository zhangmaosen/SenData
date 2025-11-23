from abc import ABC, abstractmethod
import pandas as pd
from typing import Optional

class BaseFetcher(ABC):
    """
    数据获取基类，定义统一的数据获取接口
    """
    
    @abstractmethod
    def fetch_price_history(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """获取历史价格数据 (OHLCV)"""
        pass

    @abstractmethod
    def fetch_balance_sheet(self, symbol: str) -> pd.DataFrame:
        """获取资产负债表"""
        pass

    @abstractmethod
    def fetch_cash_flow(self, symbol: str) -> pd.DataFrame:
        """获取现金流量表"""
        pass

    @abstractmethod
    def fetch_income_statement(self, symbol: str) -> pd.DataFrame:
        """获取利润表"""
        pass
    
    @abstractmethod
    def fetch_company_info(self, symbol: str) -> dict:
        """获取公司基本信息"""
        pass
    
    @abstractmethod
    def fetch_insider_transactions(self, symbol: str) -> pd.DataFrame:
        """获取内部交易记录"""
        pass
    
    @abstractmethod
    def fetch_recommendations(self, symbol: str) -> pd.DataFrame:
        """获取分析师评级"""
        pass

    @abstractmethod
    def fetch_news_sentiment(self, symbol: str) -> pd.DataFrame:
        """获取新闻及情感数据"""
        pass

    @abstractmethod
    def fetch_earnings_call_transcript(self, symbol: str, quarter: Optional[str] = None) -> str:
        """获取财报电话会议纪要"""
        pass
    
    @abstractmethod
    def fetch_advanced_analytics(self, symbol: str) -> dict:
        """获取高级分析数据"""
        pass
