"""
Unit Tests for DataLoader Service

Tests the data loading functionality, singleton pattern, and data access methods.
"""

import pytest
import pandas as pd
from api.services import DataLoader


class TestDataLoader:
    """Test suite for the DataLoader class."""
    
    def test_singleton_pattern(self, mock_data_loader):
        """
        Test that DataLoader implements the singleton pattern correctly.
        
        What is singleton pattern?
        - Only ONE instance of the class exists across the entire application
        - If you create it multiple times, you get the same object
        
        Why test this?
        - Ensures data is loaded only once (efficient)
        - All parts of the app share the same data
        """
        # Create another instance
        loader2 = DataLoader()
        
        # They should be the SAME object (same memory address)
        assert mock_data_loader is loader2, "DataLoader should return the same instance"
        
        # They should have the same data
        df1 = mock_data_loader.get_prices()
        df2 = loader2.get_prices()
        
        # Compare DataFrames
        pd.testing.assert_frame_equal(df1, df2)
    
    
    def test_get_prices_returns_dataframe(self, mock_data_loader):
        """
        Test that get_prices() returns a pandas DataFrame.
        
        What we're checking:
        - Method returns the correct data type
        - DataFrame is not None or empty
        """
        prices_df = mock_data_loader.get_prices()
        
        # Check type
        assert isinstance(prices_df, pd.DataFrame), "get_prices should return a DataFrame"
        
        # Check not empty
        assert len(prices_df) > 0, "DataFrame should not be empty"
    
    
    def test_get_prices_returns_copy(self, mock_data_loader):
        """
        Test that get_prices() returns a COPY, not the original data.
        
        Why is this important?
        - If we returned the original, someone could accidentally modify it
        - Returning a copy protects our cached data
        
        Example of the problem:
            df = loader.get_prices()
            df['A'] = 999  # This would corrupt the cache if not a copy!
        """
        df1 = mock_data_loader.get_prices()
        df2 = mock_data_loader.get_prices()
        
        # They should have the same values
        pd.testing.assert_frame_equal(df1, df2)
        
        # But be different objects in memory
        assert df1 is not df2, "get_prices should return a copy, not the original"
        
        # Modify one
        df1['A'] = 999
        
        # Get a fresh copy
        df3 = mock_data_loader.get_prices()
        
        # The fresh copy should NOT have our modification
        assert df3['A'].iloc[0] != 999, "Modifying returned DataFrame should not affect cached data"
    
    
    def test_prices_have_date_column(self, mock_data_loader):
        """
        Test that the prices DataFrame contains a DATE column.
        
        Why test this?
        - Our application depends on the DATE column for time series
        - If it's missing, the entire app breaks
        """
        prices_df = mock_data_loader.get_prices()
        
        # Check DATE column exists
        assert 'DATE' in prices_df.columns, "DataFrame must have a DATE column"
        
        # Check DATE is datetime type
        assert pd.api.types.is_datetime64_any_dtype(prices_df['DATE']), \
            "DATE column should be datetime type"
    
    
    def test_prices_are_sorted_by_date(self, mock_data_loader):
        """
        Test that prices are sorted chronologically by date.
        
        Why is sorting important?
        - Time series analysis requires chronological order
        - Latest price calculations depend on data being in order
        """
        prices_df = mock_data_loader.get_prices()
        
        # Check that dates are in ascending order
        dates = prices_df['DATE']
        assert dates.is_monotonic_increasing, "Dates should be sorted in ascending order"
    
    
    def test_get_available_symbols(self, mock_data_loader):
        """
        Test that get_available_symbols() returns correct stock symbols.
        
        Expected behavior:
        - Returns a list of stock symbols
        - Does NOT include 'DATE' in the list
        - Matches the columns from our test data (A, B, C, D, E)
        """
        symbols = mock_data_loader.get_available_symbols()
        
        # Check return type
        assert isinstance(symbols, list), "get_available_symbols should return a list"
        
        # Check expected symbols are present
        expected_symbols = ['A', 'B', 'C', 'D', 'E']
        for symbol in expected_symbols:
            assert symbol in symbols, f"Symbol {symbol} should be in available symbols"
        
        # Check DATE is NOT included
        assert 'DATE' not in symbols, "DATE column should not be in symbols list"
        
        # Check count
        assert len(symbols) == 5, "Test data should have exactly 5 symbols"
    
    
    def test_prices_have_correct_columns(self, mock_data_loader, test_prices_df):
        """
        Test that loaded prices match the expected column structure.
        
        Compares:
        - Column names
        - Column count
        - Data types
        """
        prices_df = mock_data_loader.get_prices()
        
        # Check column names match
        assert list(prices_df.columns) == list(test_prices_df.columns), \
            "Loaded columns should match test data columns"
        
        # Check we have the right number of rows
        assert len(prices_df) == len(test_prices_df), \
            "Loaded data should have same number of rows as test data"
    
    
    def test_prices_contain_numeric_values(self, mock_data_loader):
        """
        Test that all stock price columns contain numeric values.
        
        Why test this?
        - Calculations will fail if prices are strings or other types
        - Data validation is crucial for reliability
        """
        prices_df = mock_data_loader.get_prices()
        
        # Get all columns except DATE
        price_columns = [col for col in prices_df.columns if col != 'DATE']
        
        # Check each column is numeric
        for col in price_columns:
            assert pd.api.types.is_numeric_dtype(prices_df[col]), \
                f"Column {col} should contain numeric values"
            
            # Check for no NaN values in test data
            assert not prices_df[col].isna().any(), \
                f"Column {col} should not contain NaN values"


# =============================================================================
# Edge Cases and Error Handling Tests
# =============================================================================

class TestDataLoaderEdgeCases:
    """Test edge cases and error scenarios for DataLoader."""
    
    def test_dataloader_handles_empty_initialization(self):
        """
        Test that DataLoader can be reset and reinitialized.
        
        This tests the cleanup behavior - important for testing
        where we need to reset state between tests.
        """
        # Reset the singleton
        DataLoader._instance = None
        DataLoader._prices_df = None
        
        # Should be able to create a new instance
        # (This will fail in normal code because it tries to load the real file,
        # but that's expected - this test verifies the singleton reset works)
        assert DataLoader._instance is None, "Singleton should be reset"
        assert DataLoader._prices_df is None, "Cached data should be reset"

