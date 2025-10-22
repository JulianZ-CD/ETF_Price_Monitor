"""
Data loader service for loading and caching price data.
This service loads the historical prices CSV file at startup and keeps it in memory.
"""

import pandas as pd
from pathlib import Path
from typing import Optional


class DataLoader:
    """
    Singleton class to load and cache historical price data.
    The prices.csv file is loaded once at initialization and kept in memory.
    """
    
    _instance: Optional['DataLoader'] = None
    _prices_df: Optional[pd.DataFrame] = None
    
    def __new__(cls):
        """Implement singleton pattern to ensure only one instance exists."""
        if cls._instance is None:
            cls._instance = super(DataLoader, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the data loader and load prices if not already loaded."""
        if self._prices_df is None:
            self.load_prices()
    
    def load_prices(self) -> None:
        """
        Load the historical prices CSV file into memory.
        The file is expected to be in the data/ directory.
        """
        # Get the project root directory (parent of api/)
        project_root = Path(__file__).parent.parent.parent
        prices_path = project_root / "data" / "prices.csv"
        
        # Load prices and convert DATE column to datetime
        self._prices_df = pd.read_csv(prices_path)
        self._prices_df['DATE'] = pd.to_datetime(self._prices_df['DATE'])
        
        # Sort by date to ensure chronological order
        self._prices_df = self._prices_df.sort_values('DATE').reset_index(drop=True)
        
        print(f"✓ Loaded {len(self._prices_df)} rows of price data")
        print(f"✓ Date range: {self._prices_df['DATE'].min()} to {self._prices_df['DATE'].max()}")
    
    def get_prices(self) -> pd.DataFrame:
        """
        Get the cached prices DataFrame.
        
        Returns:
            pd.DataFrame: DataFrame containing historical prices with DATE column
        """
        if self._prices_df is None:
            self.load_prices()
        return self._prices_df.copy()  # Return a copy to prevent external modification
    
    def get_available_symbols(self) -> list[str]:
        """
        Get list of available constituent symbols from the prices data.
        
        Returns:
            list[str]: List of symbol names (column names excluding DATE)
        """
        if self._prices_df is None:
            self.load_prices()
        return [col for col in self._prices_df.columns if col != 'DATE']

