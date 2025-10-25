"""
Unit Tests for ETFCalculator Service

Tests the ETF price calculation logic, latest price retrieval, and top holdings analysis.
"""

import pandas as pd


class TestETFCalculator:
    """Test suite for the ETFCalculator class."""
    
    def test_calculator_initialization(self, mock_calculator):
        """
        Test that ETFCalculator initializes correctly.
        
        Checks:
        - Calculator object is created
        - Has a data_loader attribute
        """
        assert mock_calculator is not None, "Calculator should be initialized"
        assert hasattr(mock_calculator, 'data_loader'), "Calculator should have data_loader"
    
    
    def test_calculate_etf_prices_returns_dataframe(self, mock_calculator, sample_constituents):
        """
        Test that calculate_etf_prices returns a DataFrame.
        
        What this method does:
        - Takes constituent stocks and their weights
        - Calculates: ETF Price = Σ(weight × stock_price) for each date
        - Returns historical ETF prices
        """
        result = mock_calculator.calculate_etf_prices(sample_constituents)
        
        # Check return type
        assert isinstance(result, pd.DataFrame), "Should return a DataFrame"
        
        # Check has required columns
        assert 'DATE' in result.columns, "Result should have DATE column"
        assert 'etf_price' in result.columns, "Result should have etf_price column"
        
        # Check has data
        assert len(result) > 0, "Result should not be empty"
    
    
    def test_calculate_etf_prices_correct_calculation(self, mock_calculator):
        """
        Test that ETF price calculation is mathematically correct.
        
        Manual calculation example (using test data):
        - Date: 2024-01-01
        - Prices: A=100, B=50, C=75
        - Weights: A=0.5, B=0.3, C=0.2
        - Expected ETF Price = 100*0.5 + 50*0.3 + 75*0.2 = 50 + 15 + 15 = 80
        """
        # Use simple constituents for easy verification
        constituents = [
            {'name': 'A', 'weight': 0.5},
            {'name': 'B', 'weight': 0.3},
            {'name': 'C', 'weight': 0.2}
        ]
        
        result = mock_calculator.calculate_etf_prices(constituents)
        
        # Get first date's price
        first_price = result['etf_price'].iloc[0]
        
        # Manual calculation for 2024-01-01:
        # A=100, B=50, C=75 (from test_prices.csv)
        expected = 100 * 0.5 + 50 * 0.3 + 75 * 0.2
        
        # Compare with small tolerance for floating point arithmetic
        assert abs(first_price - expected) < 0.01, \
            f"Expected {expected}, got {first_price}"
    
    
    def test_calculate_etf_prices_all_dates(self, mock_calculator, sample_constituents, test_prices_df):
        """
        Test that ETF prices are calculated for all dates in the dataset.
        
        Ensures:
        - No dates are skipped
        - Date count matches input data
        """
        result = mock_calculator.calculate_etf_prices(sample_constituents)
        
        # Should have same number of dates as input data
        assert len(result) == len(test_prices_df), \
            "ETF prices should be calculated for all dates"
        
        # Dates should match
        pd.testing.assert_series_equal(
            result['DATE'].reset_index(drop=True),
            test_prices_df['DATE'].reset_index(drop=True),
            check_names=False
        )
    
    
    def test_calculate_etf_prices_with_unknown_symbol(self, mock_calculator, sample_constituents_with_unknown):
        """
        Test behavior when a constituent doesn't exist in price data.
        
        Expected behavior:
        - Should not crash
        - Should continue calculating with available symbols
        - Unknown symbols contribute 0 to the price
        """
        # This includes 'UNKNOWN' symbol which doesn't exist
        result = mock_calculator.calculate_etf_prices(sample_constituents_with_unknown)
        
        # Should still return results
        assert isinstance(result, pd.DataFrame), "Should handle unknown symbols gracefully"
        assert len(result) > 0, "Should still calculate prices"
        
        # Prices should be positive (from valid symbols)
        assert result['etf_price'].iloc[0] > 0, "Should calculate price from valid symbols"
    
    
    def test_calculate_etf_prices_weights_sum(self, mock_calculator):
        """
        Test ETF calculation with different weight sums.
        
        Note: In real ETFs, weights should sum to 1.0 (100%)
        But our code should handle any weight sum (e.g., 0.5 or 1.5)
        """
        # Weights sum to 0.5 (50%)
        constituents_half = [
            {'name': 'A', 'weight': 0.3},
            {'name': 'B', 'weight': 0.2}
        ]
        
        result_half = mock_calculator.calculate_etf_prices(constituents_half)
        
        # Should not crash and should return valid numbers
        assert len(result_half) > 0
        assert result_half['etf_price'].iloc[0] > 0


class TestGetLatestPrices:
    """Test suite for the get_latest_prices method."""
    
    def test_get_latest_prices_returns_list(self, mock_calculator, sample_constituents):
        """
        Test that get_latest_prices returns a list.
        
        This method gets the most recent price for each constituent.
        """
        result = mock_calculator.get_latest_prices(sample_constituents)
        
        # Check type
        assert isinstance(result, list), "Should return a list"
        
        # Check not empty
        assert len(result) > 0, "Should not be empty"
    
    
    def test_get_latest_prices_correct_format(self, mock_calculator, sample_constituents):
        """
        Test that each entry in the result has the correct format.
        
        Expected format:
        {
            'symbol': 'A',
            'weight': 0.3,
            'latest_price': 104.0
        }
        """
        result = mock_calculator.get_latest_prices(sample_constituents)
        
        # Check each entry has required keys
        for entry in result:
            assert 'symbol' in entry, "Each entry should have 'symbol'"
            assert 'weight' in entry, "Each entry should have 'weight'"
            assert 'latest_price' in entry, "Each entry should have 'latest_price'"
            
            # Check types
            assert isinstance(entry['symbol'], str), "Symbol should be string"
            assert isinstance(entry['weight'], (int, float)), "Weight should be numeric"
            assert isinstance(entry['latest_price'], (int, float)), "Price should be numeric"
    
    
    def test_get_latest_prices_uses_last_date(self, mock_calculator, test_prices_df):
        """
        Test that get_latest_prices uses the LAST date in the dataset.
        
        Test data has 5 dates (2024-01-01 to 2024-01-05)
        Last date is 2024-01-05 where A=104.0
        """
        constituents = [{'name': 'A', 'weight': 1.0}]
        
        result = mock_calculator.get_latest_prices(constituents)
        
        # Get the latest price for A from our test data
        expected_price = test_prices_df.iloc[-1]['A']
        
        # Should match
        assert result[0]['latest_price'] == expected_price, \
            f"Should use last date's price. Expected {expected_price}, got {result[0]['latest_price']}"
    
    
    def test_get_latest_prices_all_constituents(self, mock_calculator, sample_constituents):
        """
        Test that all constituents are included in the result.
        
        If we request 5 constituents, we should get 5 results.
        """
        result = mock_calculator.get_latest_prices(sample_constituents)
        
        # Should return entry for each constituent
        assert len(result) == len(sample_constituents), \
            "Should return price for each constituent"
        
        # Check all symbols are present
        result_symbols = {entry['symbol'] for entry in result}
        expected_symbols = {c['name'] for c in sample_constituents}
        assert result_symbols == expected_symbols, "All symbols should be present"
    
    
    def test_get_latest_prices_unknown_symbol(self, mock_calculator):
        """
        Test behavior when a constituent doesn't exist in price data.
        
        Expected: Should return 0.0 for unknown symbols.
        """
        constituents = [
            {'name': 'A', 'weight': 0.5},
            {'name': 'UNKNOWN', 'weight': 0.5}
        ]
        
        result = mock_calculator.get_latest_prices(constituents)
        
        # Find the UNKNOWN entry
        unknown_entry = next(e for e in result if e['symbol'] == 'UNKNOWN')
        
        # Should have price of 0.0
        assert unknown_entry['latest_price'] == 0.0, \
            "Unknown symbols should have price 0.0"


class TestGetTopHoldings:
    """Test suite for the get_top_holdings method."""
    
    def test_get_top_holdings_returns_list(self, mock_calculator, sample_constituents):
        """
        Test that get_top_holdings returns a list.
        
        This method calculates holding_value = weight × price
        and returns top N holdings by value.
        """
        result = mock_calculator.get_top_holdings(sample_constituents, top_n=3)
        
        assert isinstance(result, list), "Should return a list"
        assert len(result) <= 3, "Should return at most 3 holdings"
    
    
    def test_get_top_holdings_correct_format(self, mock_calculator, sample_constituents):
        """
        Test that each holding has the correct format.
        
        Expected format:
        {
            'symbol': 'A',
            'weight': 0.3,
            'latest_price': 104.0,
            'holding_value': 31.2  # 0.3 * 104.0
        }
        """
        result = mock_calculator.get_top_holdings(sample_constituents, top_n=5)
        
        for holding in result:
            # Check required keys
            assert 'symbol' in holding
            assert 'weight' in holding
            assert 'latest_price' in holding
            assert 'holding_value' in holding
            
            # Verify calculation: holding_value = weight × price
            expected_value = holding['weight'] * holding['latest_price']
            assert abs(holding['holding_value'] - expected_value) < 0.01, \
                "holding_value should equal weight × price"
    
    
    def test_get_top_holdings_sorted_by_value(self, mock_calculator, sample_constituents):
        """
        Test that holdings are sorted by value in descending order.
        
        Top holdings = largest holding_value first
        """
        result = mock_calculator.get_top_holdings(sample_constituents, top_n=5)
        
        # Extract holding values
        values = [h['holding_value'] for h in result]
        
        # Should be in descending order
        assert values == sorted(values, reverse=True), \
            "Holdings should be sorted by value (highest first)"
    
    
    def test_get_top_holdings_respects_top_n(self, mock_calculator, sample_constituents):
        """
        Test that top_n parameter limits the number of results.
        
        If we have 5 constituents but request top 3,
        we should get exactly 3 results.
        """
        # Request top 3
        result = mock_calculator.get_top_holdings(sample_constituents, top_n=3)
        assert len(result) == 3, "Should return exactly 3 holdings"
        
        # Request top 2
        result = mock_calculator.get_top_holdings(sample_constituents, top_n=2)
        assert len(result) == 2, "Should return exactly 2 holdings"
        
        # Request more than available
        result = mock_calculator.get_top_holdings(sample_constituents, top_n=10)
        assert len(result) == 5, "Should return all available holdings (5)"
    
    
    def test_get_top_holdings_calculation(self, mock_calculator):
        """
        Test that holding value calculation is correct.
        
        Manual calculation:
        - A: weight=0.3, price=104.0 → value=31.2
        - E: weight=0.1, price=154.0 → value=15.4
        """
        constituents = [
            {'name': 'A', 'weight': 0.3},  # 104 * 0.3 = 31.2
            {'name': 'E', 'weight': 0.1}   # 154 * 0.1 = 15.4
        ]
        
        result = mock_calculator.get_top_holdings(constituents, top_n=2)
        
        # A should be first (larger value)
        assert result[0]['symbol'] == 'A', "A should have highest holding value"
        assert abs(result[0]['holding_value'] - 31.2) < 0.01
        
        # E should be second
        assert result[1]['symbol'] == 'E'
        assert abs(result[1]['holding_value'] - 15.4) < 0.01
    
    
    def test_get_top_holdings_default_top_n(self, mock_calculator, sample_constituents):
        """
        Test that default top_n is 5.
        
        When top_n is not specified, should default to 5.
        """
        result = mock_calculator.get_top_holdings(sample_constituents)
        
        # Should return 5 (or all available if less than 5)
        assert len(result) <= 5, "Default should be top 5"

