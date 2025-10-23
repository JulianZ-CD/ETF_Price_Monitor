"""
Calculator service for ETF price computations.
Handles weighted sum calculations and top holdings analysis.
"""

import pandas as pd
from typing import List, Dict, Any
from .data_loader import DataLoader


class ETFCalculator:
    """
    Service class for calculating ETF prices and analytics.
    """
    
    def __init__(self):
        """Initialize calculator with data loader."""
        self.data_loader = DataLoader()
    
    def calculate_etf_prices(self, constituents: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Calculate historical ETF prices based on constituent weights.
        ETF Price = Σ(weight × constituent_price) for each date
        
        Args:
            constituents: List of dicts with 'name' and 'weight' keys
            
        Returns:
            pd.DataFrame: DataFrame with 'DATE' and 'etf_price' columns
        """
        prices_df = self.data_loader.get_prices()
        
        # Create a copy with just the DATE column
        etf_prices = prices_df[['DATE']].copy()
        
        # Calculate weighted sum for each constituent
        etf_prices['etf_price'] = 0.0
        
        for constituent in constituents:
            symbol = constituent['name']
            weight = constituent['weight']
            
            # Check if symbol exists in price data
            if symbol in prices_df.columns:
                # Add weighted price to ETF price
                etf_prices['etf_price'] += prices_df[symbol] * weight
            else:
                print(f"⚠ Warning: Symbol {symbol} not found in price data")
        
        return etf_prices
    
    def get_latest_prices(self, constituents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Get the latest price for each constituent.
        
        Args:
            constituents: List of dicts with 'name' and 'weight' keys
            
        Returns:
            List of dicts with 'symbol', 'weight', and 'latest_price' keys
        """
        prices_df = self.data_loader.get_prices()
        
        # Get the last row (most recent date)
        latest_prices_row = prices_df.iloc[-1]
        
        result = []
        for constituent in constituents:
            symbol = constituent['name']
            weight = constituent['weight']
            
            # Get latest price for this symbol
            latest_price = latest_prices_row.get(symbol, 0.0) if symbol in prices_df.columns else 0.0
            
            result.append({
                'symbol': symbol,
                'weight': weight,
                'latest_price': float(latest_price)
            })
        
        return result
    
    def get_top_holdings(self, constituents: List[Dict[str, Any]], top_n: int = 5) -> List[Dict[str, Any]]:
        """
        Calculate and return the top N holdings by market value.
        Holding value = weight × latest_price
        
        Args:
            constituents: List of dicts with 'name' and 'weight' keys
            top_n: Number of top holdings to return (default: 5)
            
        Returns:
            List of dicts with 'symbol', 'weight', 'latest_price', and 'holding_value' keys,
            sorted by holding_value in descending order
        """
        prices_df = self.data_loader.get_prices()
        
        # Get the last row (most recent date)
        latest_prices_row = prices_df.iloc[-1]
        
        holdings = []
        for constituent in constituents:
            symbol = constituent['name']
            weight = constituent['weight']
            
            # Get latest price for this symbol
            latest_price = latest_prices_row.get(symbol, 0.0) if symbol in prices_df.columns else 0.0
            
            # Calculate holding value (weight × price)
            holding_value = weight * float(latest_price)
            
            holdings.append({
                'symbol': symbol,
                'weight': weight,
                'latest_price': float(latest_price),
                'holding_value': holding_value
            })
        
        # Sort by holding_value in descending order and return top N
        holdings.sort(key=lambda x: x['holding_value'], reverse=True)
        return holdings[:top_n]

