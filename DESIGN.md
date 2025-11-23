# SenData 项目设计文档

## 1. 项目概述 (Project Overview)

*   **项目名称**: SenData (森的数据工具)
*   **版本**: 0.1.0 (Draft)
*   **维护者**: 森 (Sen)
*   **状态**: 规划中

### 1.1 背景与目标
SenData 是一个专注于股票数据获取与服务的工具库。它的核心使命是为 AI Agent 生态系统提供可靠的金融数据支持。
主要解决两个核心需求：
1.  **离线/批量数据支持**：构建历史数据仓库，供 Agent 进行训练、回测或深度分析。
2.  **在线/实时数据支持**：提供易用的 Python Library，让 Agent 能够在运行时实时查询市场状态。

### 1.2 核心功能 (Key Features)

#### A. 批量数据采集 (Batch Collector)
参考 `TauricResearch/TradingAgents` 的数据流设计，我们将支持以下数据类型的批量采集与本地缓存：

1.  **市场行情数据 (Market Data)**
    *   **OHLCV**: 开盘、最高、最低、收盘、成交量 (支持日/周/月频度)。
    *   **技术指标 (Technical Indicators)**: 基于 `stockstats` 计算常见指标 (MACD, RSI, Bollinger Bands, ATR, SMA/EMA 等)。
2.  **基本面数据 (Fundamental Data)**
    *   **资产负债表 (Balance Sheet)**: 年度/季度。
    *   **现金流量表 (Cash Flow)**: 年度/季度。
    *   **利润表 (Income Statement)**: 年度/季度。
    *   **公司信息 (Company Info)**: 行业、板块、市值、简介等。
    *   **分红派息 (Dividends)**: 历史分红记录。
3.  **另类数据 (Alternative Data)**
    *   **内部交易 (Insider Transactions)**: 公司内部人员交易记录。
    *   **分析师评级 (Analyst Recommendations)**: 机构评级趋势。
    *   **新闻 (News)**: (可选) 个股相关新闻。

*   **数据源**: 
    *   首选 **`yfinance`** (覆盖上述大部分数据)。
    *   预留 **`Alpha Vantage`** 接口 (用于补充新闻或更详细的财务数据)。
*   **存储方式**: 
    *   本地文件系统: `data/{symbol}/{category}_{frequency}.csv`

#### B. 实时数据接口 (Real-time Library)
*   提供 Python SDK 供外部项目直接 `import` 调用。
*   功能包括：
    *   获取当前最新价格/行情。
    *   获取当天的分时数据。
    *   查询个股基础信息。

## 2. 系统架构 (System Architecture)

### 2.1 技术栈 (Tech Stack)
*   **核心语言**: Python 3.x
*   **数据处理**: Pandas, NumPy
*   **数据源 (潜在)**: AkShare, Tushare, YFinance, ccxt (视具体市场而定)
*   **存储层**: 
    *   文件存储: CSV / Parquet (适合批量导出)
    *   数据库: SQLite (轻量级) 或 PostgreSQL (生产级)

### 2.2 模块划分 (Module Design)
```
src/
├── main.py             # CLI 入口 (用于触发批量任务)
├── fetcher/            # 数据获取层 (适配不同的数据源)
│   ├── __init__.py
│   ├── base.py         # 定义获取数据的接口规范
│   └── stock_source.py # 具体实现 (如 akshare/yfinance)
├── storage/            # 数据存储层
│   ├── __init__.py
│   └── saver.py        # 负责写入 CSV/DB
└── lib/                # 对外暴露的 SDK 接口
    ├── __init__.py
    └── api.py          # Agent 调用的主要入口
```

## 3. 数据设计 (Data Design)
*   **存储格式**: 优先支持 CSV/Parquet 以便与其他数据科学工具兼容。
*   **目录规范**:
    *   `data/raw/`: 原始下载数据
    *   `data/processed/`: 清洗后的标准化数据

## 4. 接口设计 (API Design)

### 4.1 外部 Agent 调用示例
```python
from sendata.lib import SenStock

# 初始化
stock = SenStock(symbol="AAPL")

# 获取实时价格
price = stock.get_current_price()

# 获取历史数据
history = stock.get_history(days=30)
```

## 5. 开发计划 (Roadmap)
*   **阶段一：原型验证**
    *   选定一个数据源库 (如 AkShare 或 YFinance)。
    *   实现简单的“获取并打印”功能。
*   **阶段二：SDK 封装**
    *   完成 `lib` 模块，供外部 import 使用。
*   **阶段三：批量采集器**
    *   实现 CLI 工具，支持 `python main.py --batch-download`。
    *   实现数据保存到 CSV。

## 6. 数据源与数据类型 (Data Sources & Data Types)

### 6.1 数据源 (Data Sources)
- **Primary**: `yfinance` (Yahoo Finance) - 免费，覆盖面广，包含价格、基本面、期权等。
- **Secondary**: `Alpha Vantage` - 提供 Alpha Intelligence 数据 (新闻情感, 财报会议纪要, 内部交易, 高级分析等)。

### 6.2 数据类型 (Data Types)
#### 6.2.1 市场数据 (Market Data)
- **OHLCV**: Open, High, Low, Close, Volume (Daily/Intraday)
- **Technical Indicators**: MA, RSI, MACD, Bollinger Bands, etc. (via `stockstats` or Alpha Vantage)
- **Market Status**: Top Gainers/Losers (Alpha Vantage)

#### 6.2.2 基本面数据 (Fundamental Data)
- **Financial Statements**: Balance Sheet, Income Statement, Cash Flow
- **Company Info**: Sector, Industry, Market Cap, Employees, Description
- **Earnings**: Earnings History, Earnings Calendar (Alpha Vantage)

#### 6.2.3 Alpha Intelligence (New)
- **News & Sentiment**: 市场新闻及情感分析 (Alpha Vantage)
- **Earnings Call Transcripts**: 财报电话会议纪要 (Alpha Vantage)
- **Insider Transactions**: 内部人士交易记录 (Alpha Vantage/yfinance)
- **Advanced Analytics**: 估值、波动率等高级分析 (Alpha Vantage)
