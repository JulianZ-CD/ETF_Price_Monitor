"""
Pytest configuration and shared fixtures.

This file contains fixtures that are available to all tests.
Fixtures are reusable components that help set up test conditions.
"""

import pytest
import pandas as pd
from pathlib import Path
from fastapi.testclient import TestClient
from unittest.mock import patch
import sys

# Add the parent directory to the path so we can import api modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from api.services import DataLoader, ETFCalculator
from api.index import app


# =============================================================================
# Path Fixtures - Provide paths to test data files
# =============================================================================

@pytest.fixture
def test_data_dir():
    """
    Returns the path to the test_data directory.
    This fixture helps locate test CSV files.
    """
    return Path(__file__).parent / "test_data"


@pytest.fixture
def test_prices_csv(test_data_dir):
    """
    Returns the path to the test prices CSV file.
    This is a small dataset with 5 stocks and 5 days for fast testing.
    """
    return test_data_dir / "test_prices.csv"


@pytest.fixture
def test_etf_valid_csv(test_data_dir):
    """
    Returns the path to a valid ETF constituents CSV file.
    Contains proper 'name' and 'weight' columns.
    """
    return test_data_dir / "test_etf_valid.csv"


@pytest.fixture
def test_etf_invalid_csv(test_data_dir):
    """
    Returns the path to an invalid ETF constituents CSV file.
    Missing required columns - used for testing error handling.
    """
    return test_data_dir / "test_etf_invalid.csv"


# =============================================================================
# DataLoader Fixtures - Provide test instances of DataLoader
# =============================================================================

@pytest.fixture
def mock_data_loader(test_prices_csv):
    """
    Creates a DataLoader instance that uses test data instead of real data.
    
    This fixture uses Python's 'patch' to temporarily replace the real
    prices.csv path with our test data path.
    
    Why mock? We want tests to:
    1. Run fast (small test data)
    2. Be predictable (known test values)
    3. Not depend on external files that might change
    """
    # Reset the DataLoader singleton before each test
    DataLoader._instance = None
    DataLoader._prices_df = None
    
    # Create a custom load function that uses test data
    original_load = DataLoader.load_prices
    
    def load_test_prices(self):
        """Load test prices instead of real prices."""
        self._prices_df = pd.read_csv(test_prices_csv)
        self._prices_df['DATE'] = pd.to_datetime(self._prices_df['DATE'])
        self._prices_df = self._prices_df.sort_values('DATE').reset_index(drop=True)
    
    # Temporarily replace the load_prices method
    DataLoader.load_prices = load_test_prices
    
    try:
        loader = DataLoader()
        yield loader
    finally:
        # Clean up: Reset singleton and restore original method
        DataLoader.load_prices = original_load
        DataLoader._instance = None
        DataLoader._prices_df = None


@pytest.fixture
def test_prices_df(test_prices_csv):
    """
    Loads the test prices CSV as a pandas DataFrame.
    
    Useful for tests that need direct access to the data
    without going through DataLoader.
    """
    df = pd.read_csv(test_prices_csv)
    df['DATE'] = pd.to_datetime(df['DATE'])
    return df


# =============================================================================
# Calculator Fixtures - Provide test instances of ETFCalculator
# =============================================================================

@pytest.fixture
def mock_calculator(mock_data_loader):
    """
    Creates an ETFCalculator instance that uses mocked test data.
    
    This calculator will use the mock_data_loader, so all calculations
    will be based on our small test dataset.
    """
    # Patch the DataLoader inside Calculator to use our mock
    with patch('api.services.calculator.DataLoader', return_value=mock_data_loader):
        calculator = ETFCalculator()
        # Override the data_loader attribute
        calculator.data_loader = mock_data_loader
        yield calculator


# =============================================================================
# Test Data Fixtures - Provide sample constituents data
# =============================================================================

@pytest.fixture
def sample_constituents():
    """
    Provides sample ETF constituents data for testing.
    
    This matches the stocks in test_prices.csv with known weights.
    Format: [{'name': 'A', 'weight': 0.3}, ...]
    """
    return [
        {'name': 'A', 'weight': 0.3},
        {'name': 'B', 'weight': 0.2},
        {'name': 'C', 'weight': 0.25},
        {'name': 'D', 'weight': 0.15},
        {'name': 'E', 'weight': 0.1}
    ]


@pytest.fixture
def sample_constituents_with_unknown():
    """
    Provides constituents that include a non-existent stock.
    
    Used for testing error handling when a constituent
    doesn't exist in the price data.
    """
    return [
        {'name': 'A', 'weight': 0.4},
        {'name': 'B', 'weight': 0.3},
        {'name': 'UNKNOWN', 'weight': 0.3}  # This stock doesn't exist
    ]


# =============================================================================
# API Test Fixtures - Provide FastAPI test client
# =============================================================================

@pytest.fixture
def test_client(mock_data_loader):
    """
    Provides a FastAPI test client for integration testing.
    
    TestClient allows us to make HTTP requests to the API
    without actually starting a server.
    
    Usage in tests:
        response = test_client.post("/api/py/v1/etfs", files=...)
        assert response.status_code == 200
    """
    # Patch DataLoader in the actual router module
    with patch('api.routers.etf_router.DataLoader', return_value=mock_data_loader):
        # Also patch the calculator's DataLoader
        with patch('api.services.calculator.DataLoader', return_value=mock_data_loader):
            client = TestClient(app)
            yield client


# =============================================================================
# Pytest Configuration
# =============================================================================

def pytest_configure(config):
    """
    Pytest hook that runs before any tests.
    Can be used for global test configuration.
    """
    # Add custom markers (optional)
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )

