import os
import pandas as pd
import json

class FileSaver:
    def __init__(self, base_dir="data"):
        self.base_dir = base_dir

    def _get_dir(self, symbol: str):
        path = os.path.join(self.base_dir, symbol)
        os.makedirs(path, exist_ok=True)
        return path

    def save_dataframe(self, symbol: str, name: str, df: pd.DataFrame, merge: bool = True):
        if df is None or df.empty:
            print(f"Skipping save for {symbol} - {name}: Data is empty")
            return
        
        path = os.path.join(self._get_dir(symbol), f"{name}.csv")
        
        # Merge logic for specific data types
        if merge and os.path.exists(path):
            try:
                if name == "price_history":
                    # Row-based merge for Time Series (Index is Date)
                    old_df = pd.read_csv(path, index_col=0, parse_dates=True)
                    if isinstance(df.index, pd.DatetimeIndex):
                        # Ensure new df index is timezone-naive or matches old_df
                        # yfinance often returns timezone-aware. CSV read is usually naive unless parsed carefully.
                        # Let's convert both to timezone-naive for simplicity if needed, or keep as is.
                        # Simplest: concat and let pandas handle it, then drop duplicates.
                        combined = pd.concat([old_df, df])
                        # Remove duplicates based on index, keeping the new one (last)
                        combined = combined[~combined.index.duplicated(keep='last')]
                        combined = combined.sort_index()
                        df = combined
                        
                elif name in ["balance_sheet", "cash_flow", "income_statement"]:
                    # Column-based merge for Financials (Columns are Dates)
                    old_df = pd.read_csv(path, index_col=0)
                    
                    # Convert new df columns to string to match CSV columns
                    df.columns = df.columns.astype(str)
                    
                    # Combine: update old with new, add new columns
                    # axis=1 concat
                    combined = pd.concat([old_df, df], axis=1)
                    # Remove duplicate columns (dates), keeping the new one (last)
                    combined = combined.loc[:, ~combined.columns.duplicated(keep='last')]
                    # Sort columns (dates) descending usually for financials
                    try:
                        combined = combined.sort_index(axis=1, ascending=False)
                    except:
                        pass
                    df = combined
                    
            except Exception as e:
                print(f"Warning: Could not merge with existing {name}.csv: {e}. Overwriting.")

        df.to_csv(path)
        print(f"Saved {name} for {symbol} to {path}")

    def save_json(self, symbol: str, name: str, data: dict):
        if not data:
            print(f"Skipping save for {symbol} - {name}: Data is empty")
            return

        path = os.path.join(self._get_dir(symbol), f"{name}.json")
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, default=str)
        print(f"Saved {name} for {symbol} to {path}")
