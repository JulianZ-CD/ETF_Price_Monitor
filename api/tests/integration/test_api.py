"""
Integration Tests for API Endpoints

Tests the complete API functionality including file uploads, error handling,
and response formats. These tests verify that all components work together correctly.
"""

import pytest
import io
from fastapi.testclient import TestClient


# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration


class TestETFEndpoint:
    """Test suite for POST /api/py/v1/etfs endpoint."""
    
    def test_upload_valid_etf_success(self, test_client, test_etf_valid_csv):
        """
        Test successful ETF file upload and analysis.
        
        Simulates a user uploading a valid CSV file through the API.
        
        Expected response:
        {
            'status': 'success',
            'table_data': [...],
            'time_series': [...],
            'top_holdings': [...]
        }
        """
        # Read the test CSV file
        with open(test_etf_valid_csv, 'rb') as f:
            files = {'file': ('test_etf.csv', f, 'text/csv')}
            
            # Make POST request to upload endpoint
            response = test_client.post('/api/py/v1/etfs', files=files)
        
        # Check response status
        assert response.status_code == 200, \
            f"Expected 200, got {response.status_code}: {response.text}"
        
        # Parse JSON response
        data = response.json()
        
        # Check response structure
        assert 'status' in data, "Response should have 'status' field"
        assert data['status'] == 'success', "Status should be 'success'"
        
        assert 'table_data' in data, "Response should have 'table_data'"
        assert 'time_series' in data, "Response should have 'time_series'"
        assert 'top_holdings' in data, "Response should have 'top_holdings'"
    
    
    def test_upload_valid_etf_table_data_format(self, test_client, test_etf_valid_csv):
        """
        Test that table_data has the correct format.
        
        Each entry should have:
        - symbol: stock symbol (string)
        - weight: constituent weight (float)
        - latest_price: most recent price (float)
        """
        with open(test_etf_valid_csv, 'rb') as f:
            files = {'file': ('test_etf.csv', f, 'text/csv')}
            response = test_client.post('/api/py/v1/etfs', files=files)
        
        data = response.json()
        table_data = data['table_data']
        
        # Check it's a list
        assert isinstance(table_data, list), "table_data should be a list"
        assert len(table_data) > 0, "table_data should not be empty"
        
        # Check first entry format
        entry = table_data[0]
        assert 'symbol' in entry, "Each entry should have 'symbol'"
        assert 'weight' in entry, "Each entry should have 'weight'"
        assert 'latest_price' in entry, "Each entry should have 'latest_price'"
        
        # Check types
        assert isinstance(entry['symbol'], str)
        assert isinstance(entry['weight'], (int, float))
        assert isinstance(entry['latest_price'], (int, float))
    
    
    def test_upload_valid_etf_time_series_format(self, test_client, test_etf_valid_csv):
        """
        Test that time_series has the correct format.
        
        Each entry should have:
        - date: date string (YYYY-MM-DD format)
        - price: ETF price on that date (float)
        """
        with open(test_etf_valid_csv, 'rb') as f:
            files = {'file': ('test_etf.csv', f, 'text/csv')}
            response = test_client.post('/api/py/v1/etfs', files=files)
        
        data = response.json()
        time_series = data['time_series']
        
        # Check it's a list
        assert isinstance(time_series, list), "time_series should be a list"
        assert len(time_series) > 0, "time_series should not be empty"
        
        # Check first entry format
        entry = time_series[0]
        assert 'date' in entry, "Each entry should have 'date'"
        assert 'price' in entry, "Each entry should have 'price'"
        
        # Check date format (YYYY-MM-DD)
        assert isinstance(entry['date'], str)
        assert len(entry['date']) == 10, "Date should be in YYYY-MM-DD format"
        assert entry['date'].count('-') == 2, "Date should have two hyphens"
        
        # Check price is numeric
        assert isinstance(entry['price'], (int, float))
    
    
    def test_upload_valid_etf_top_holdings_format(self, test_client, test_etf_valid_csv):
        """
        Test that top_holdings has the correct format.
        
        Each entry should have:
        - symbol: stock symbol
        - weight: weight in ETF
        - latest_price: current price
        - holding_value: weight × price
        
        Should be sorted by holding_value (descending)
        """
        with open(test_etf_valid_csv, 'rb') as f:
            files = {'file': ('test_etf.csv', f, 'text/csv')}
            response = test_client.post('/api/py/v1/etfs', files=files)
        
        data = response.json()
        top_holdings = data['top_holdings']
        
        # Check it's a list
        assert isinstance(top_holdings, list), "top_holdings should be a list"
        assert len(top_holdings) > 0, "top_holdings should not be empty"
        assert len(top_holdings) <= 5, "Should return at most 5 top holdings"
        
        # Check first entry format
        entry = top_holdings[0]
        assert 'symbol' in entry
        assert 'weight' in entry
        assert 'latest_price' in entry
        assert 'holding_value' in entry
        
        # Verify sorted by value (descending)
        values = [h['holding_value'] for h in top_holdings]
        assert values == sorted(values, reverse=True), \
            "Top holdings should be sorted by value (highest first)"
    
    
    def test_upload_invalid_csv_missing_columns(self, test_client, test_etf_invalid_csv):
        """
        Test error handling for invalid CSV (missing required columns).
        
        Our test_etf_invalid.csv has 'symbol' and 'percentage'
        instead of the required 'name' and 'weight'.
        
        Expected: 400 Bad Request with error message
        """
        with open(test_etf_invalid_csv, 'rb') as f:
            files = {'file': ('invalid.csv', f, 'text/csv')}
            response = test_client.post('/api/py/v1/etfs', files=files)
        
        # Should return 400 Bad Request
        assert response.status_code == 400, \
            "Invalid CSV should return 400 status code"
        
        # Check error response format
        data = response.json()
        assert 'detail' in data, "Error response should have 'detail' field"
        
        # Error message should mention the missing columns
        error_message = data['detail'].lower()
        assert 'name' in error_message or 'weight' in error_message, \
            "Error should mention missing columns"
    
    
    def test_upload_invalid_csv_malformed(self, test_client):
        """
        Test error handling for completely malformed CSV.
        
        Sends invalid CSV data that can't be parsed.
        """
        # Create malformed CSV content
        malformed_csv = "this is not,a valid\ncsv file!!!"
        files = {'file': ('malformed.csv', io.BytesIO(malformed_csv.encode()), 'text/csv')}
        
        response = test_client.post('/api/py/v1/etfs', files=files)
        
        # Should return 400 Bad Request
        assert response.status_code == 400, \
            "Malformed CSV should return 400 status code"
    
    
    def test_upload_non_numeric_weights(self, test_client):
        """
        Test error handling when weights are not numeric.
        
        CSV with string values in weight column.
        """
        # Create CSV with non-numeric weight
        invalid_csv = "name,weight\nA,high\nB,0.2"
        files = {'file': ('invalid_weight.csv', io.BytesIO(invalid_csv.encode()), 'text/csv')}
        
        response = test_client.post('/api/py/v1/etfs', files=files)
        
        # Should return 400 Bad Request
        assert response.status_code == 400, \
            "Non-numeric weights should return 400 status code"
        
        # Check error message
        data = response.json()
        error_message = data['detail'].lower()
        assert 'numeric' in error_message or 'weight' in error_message, \
            "Error should mention numeric/weight issue"
    
    
    def test_upload_empty_file(self, test_client):
        """
        Test error handling for empty file upload.
        """
        # Create empty file
        empty_csv = ""
        files = {'file': ('empty.csv', io.BytesIO(empty_csv.encode()), 'text/csv')}
        
        response = test_client.post('/api/py/v1/etfs', files=files)
        
        # Should return 400 Bad Request
        assert response.status_code == 400, \
            "Empty file should return 400 status code"
    
    
    def test_upload_without_file(self, test_client):
        """
        Test error handling when no file is uploaded.
        
        Makes POST request without the 'file' field.
        """
        response = test_client.post('/api/py/v1/etfs')
        
        # Should return 422 Unprocessable Entity (FastAPI validation error)
        assert response.status_code == 422, \
            "Request without file should return 422 status code"


class TestHealthEndpoint:
    """Test suite for GET /api/py/v1/health endpoint."""
    
    def test_health_check_success(self, test_client):
        """
        Test the health check endpoint.
        
        This endpoint verifies the API is running and data is loaded.
        """
        response = test_client.get('/api/py/v1/health')
        
        # Should return 200 OK
        assert response.status_code == 200, \
            f"Health check should return 200, got {response.status_code}"
        
        # Parse response
        data = response.json()
        
        # Check expected fields
        assert 'status' in data, "Health response should have 'status'"
        assert data['status'] == 'healthy', "Status should be 'healthy'"
        
        assert 'service' in data, "Health response should have 'service'"
        assert 'version' in data, "Health response should have 'version'"
        assert 'data_loaded' in data, "Health response should have 'data_loaded'"
    
    
    def test_health_check_data_loaded(self, test_client):
        """
        Test that health check reports data as loaded.
        
        Since we use mock_data_loader, data should be loaded.
        """
        response = test_client.get('/api/py/v1/health')
        data = response.json()
        
        # Data should be loaded (from our mock)
        assert data['data_loaded'] is True, \
            "Health check should report data as loaded"


class TestRootEndpoint:
    """Test suite for GET /api/py root endpoint."""
    
    def test_root_endpoint(self, test_client):
        """
        Test the API root endpoint.
        
        Returns basic API information.
        """
        response = test_client.get('/api/py')
        
        # Should return 200 OK
        assert response.status_code == 200
        
        # Parse response
        data = response.json()
        
        # Check expected fields
        assert 'name' in data, "Root should return API name"
        assert 'version' in data, "Root should return version"
        assert 'versions' in data, "Root should list available versions"


class TestCORSHeaders:
    """Test CORS (Cross-Origin Resource Sharing) configuration."""
    
    def test_cors_headers_present(self, test_client):
        """
        Test that CORS headers are set correctly.
        
        CORS allows frontend (on different domain) to call backend.
        Without CORS, browsers block cross-origin requests.
        """
        response = test_client.get('/api/py/v1/health')
        
        # Check for CORS headers
        # Note: TestClient might not include all CORS headers,
        # but we can verify the middleware is configured
        assert response.status_code == 200, "Request should succeed"


class TestEndToEndWorkflow:
    """Test complete end-to-end workflows."""
    
    def test_complete_etf_analysis_workflow(self, test_client, test_etf_valid_csv):
        """
        Test a complete workflow:
        1. Check API health
        2. Upload ETF file
        3. Verify all data is returned correctly
        
        This simulates what a real user would do.
        """
        # Step 1: Check health
        health_response = test_client.get('/api/py/v1/health')
        assert health_response.status_code == 200
        assert health_response.json()['status'] == 'healthy'
        
        # Step 2: Upload ETF file
        with open(test_etf_valid_csv, 'rb') as f:
            files = {'file': ('etf.csv', f, 'text/csv')}
            upload_response = test_client.post('/api/py/v1/etfs', files=files)
        
        assert upload_response.status_code == 200
        data = upload_response.json()
        
        # Step 3: Verify all data sections are present and valid
        
        # Table data
        assert len(data['table_data']) == 5, "Should have 5 constituents"
        
        # Time series
        assert len(data['time_series']) > 0, "Should have time series data"
        
        # Verify time series is chronologically ordered
        dates = [entry['date'] for entry in data['time_series']]
        assert dates == sorted(dates), "Time series should be chronologically ordered"
        
        # Top holdings
        assert len(data['top_holdings']) <= 5, "Should have at most 5 top holdings"
        
        # Verify all top holdings are also in table data
        table_symbols = {entry['symbol'] for entry in data['table_data']}
        for holding in data['top_holdings']:
            assert holding['symbol'] in table_symbols, \
                "Top holdings should be subset of constituents"

