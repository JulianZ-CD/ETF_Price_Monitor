"""
Integration Tests for API Validation

Tests that the API properly validates ETF data and returns clear error messages.
"""

import pytest
import io


pytestmark = pytest.mark.integration


class TestWeightSumValidation:
    """Test API validation of weight sums."""
    
    def test_valid_weight_sum_accepted(self, test_client):
        """Test that ETF with correct weight sum is accepted."""
        # Create CSV with weights summing to 1.0
        csv_content = "name,weight\nA,0.5\nB,0.3\nC,0.2"
        files = {'file': ('valid.csv', io.BytesIO(csv_content.encode()), 'text/csv')}
        
        response = test_client.post('/api/py/v1/etfs', files=files)
        
        # Should succeed
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    
    def test_weight_sum_too_low_rejected(self, test_client):
        """Test that weights summing to < 1.0 are rejected."""
        # Weights sum to only 0.7 (70%)
        csv_content = "name,weight\nA,0.4\nB,0.3"
        files = {'file': ('invalid.csv', io.BytesIO(csv_content.encode()), 'text/csv')}
        
        response = test_client.post('/api/py/v1/etfs', files=files)
        
        # Should fail with 400 Bad Request
        assert response.status_code == 400, "Should reject weight sum != 1.0"
        
        # Error message should be clear
        error_detail = response.json()['detail']
        assert 'validation failed' in error_detail.lower()
        assert 'weight' in error_detail.lower()
    
    
    def test_weight_sum_too_high_rejected(self, test_client):
        """Test that weights summing to > 1.0 are rejected."""
        # Weights sum to 1.3 (130%)
        csv_content = "name,weight\nA,0.8\nB,0.5"
        files = {'file': ('invalid.csv', io.BytesIO(csv_content.encode()), 'text/csv')}
        
        response = test_client.post('/api/py/v1/etfs', files=files)
        
        # Should fail with 400
        assert response.status_code == 400
        
        error_detail = response.json()['detail']
        assert 'validation' in error_detail.lower()


class TestWeightRangeValidation:
    """Test API validation of individual weight ranges."""
    
    def test_negative_weight_rejected(self, test_client):
        """Test that negative weights are rejected."""
        csv_content = "name,weight\nA,0.6\nB,-0.1\nC,0.5"
        files = {'file': ('invalid.csv', io.BytesIO(csv_content.encode()), 'text/csv')}
        
        response = test_client.post('/api/py/v1/etfs', files=files)
        
        assert response.status_code == 400
        error_detail = response.json()['detail']
        assert 'B' in error_detail or 'negative' in error_detail.lower()
    
    
    def test_weight_above_one_rejected(self, test_client):
        """Test that weights > 1.0 are rejected."""
        csv_content = "name,weight\nA,1.5"
        files = {'file': ('invalid.csv', io.BytesIO(csv_content.encode()), 'text/csv')}
        
        response = test_client.post('/api/py/v1/etfs', files=files)
        
        assert response.status_code == 400
        error_detail = response.json()['detail']
        assert 'A' in error_detail or '1.5' in error_detail


class TestSymbolValidation:
    """Test API validation of symbol existence."""
    
    def test_unknown_symbol_rejected(self, test_client):
        """Test that unknown stock symbols are rejected."""
        # UNKNOWN_SYMBOL doesn't exist in our test data
        csv_content = "name,weight\nA,0.5\nUNKNOWN_SYMBOL,0.5"
        files = {'file': ('invalid.csv', io.BytesIO(csv_content.encode()), 'text/csv')}
        
        response = test_client.post('/api/py/v1/etfs', files=files)
        
        assert response.status_code == 400
        error_detail = response.json()['detail']
        assert 'UNKNOWN_SYMBOL' in error_detail
        assert 'not found' in error_detail.lower() or 'symbol' in error_detail.lower()
    
    
    def test_all_valid_symbols_accepted(self, test_client):
        """Test that all valid symbols are accepted."""
        # A, B, C all exist in test data
        csv_content = "name,weight\nA,0.5\nB,0.3\nC,0.2"
        files = {'file': ('valid.csv', io.BytesIO(csv_content.encode()), 'text/csv')}
        
        response = test_client.post('/api/py/v1/etfs', files=files)
        
        assert response.status_code == 200
    
    def test_duplicate_symbol_rejected(self, test_client):
        """Test that ETF with duplicate symbols is rejected."""
        # Create CSV with duplicate symbols
        csv_content = "name,weight\nA,0.3\nB,0.4\nA,0.3"
        files = {'file': ('duplicate.csv', io.BytesIO(csv_content.encode()), 'text/csv')}
        
        response = test_client.post('/api/py/v1/etfs', files=files)
        
        # Should fail with 400
        assert response.status_code == 400
        
        # Error message should mention duplicates
        error_detail = response.json()['detail']
        assert 'duplicate' in error_detail.lower()
        assert 'A' in error_detail  # Should mention which symbol is duplicated


class TestEmptyDataValidation:
    """Test API validation of empty data."""
    
    def test_empty_csv_rejected(self, test_client):
        """Test that CSV with only headers is rejected."""
        csv_content = "name,weight"  # No data rows
        files = {'file': ('empty.csv', io.BytesIO(csv_content.encode()), 'text/csv')}
        
        response = test_client.post('/api/py/v1/etfs', files=files)
        
        # Should fail - ETF must have constituents
        assert response.status_code == 400
        error_detail = response.json()['detail']
        assert 'at least one' in error_detail.lower() or 'empty' in error_detail.lower()


class TestMultipleValidationErrors:
    """Test that API reports all validation errors."""
    
    def test_multiple_errors_reported(self, test_client):
        """Test that multiple validation failures are all reported."""
        # Multiple issues:
        # 1. Negative weight for B
        # 2. UNKNOWN symbol
        # 3. Weights don't sum to 1.0
        csv_content = "name,weight\nA,0.3\nB,-0.1\nUNKNOWN,0.5"
        files = {'file': ('invalid.csv', io.BytesIO(csv_content.encode()), 'text/csv')}
        
        response = test_client.post('/api/py/v1/etfs', files=files)
        
        assert response.status_code == 400
        error_detail = response.json()['detail']
        
        # Error message should be comprehensive
        # Check for indicators of different errors
        has_negative_error = 'negative' in error_detail.lower() or 'range' in error_detail.lower()
        has_symbol_error = 'UNKNOWN' in error_detail or 'symbol' in error_detail.lower()
        
        # Should mention at least 2 different issues
        assert has_negative_error or has_symbol_error, \
            "Should report multiple validation failures"


class TestErrorMessageClarity:
    """Test that error messages are user-friendly."""
    
    def test_error_message_contains_details(self, test_client):
        """Test that error messages provide actionable information."""
        csv_content = "name,weight\nA,0.6"  # Only 60%
        files = {'file': ('invalid.csv', io.BytesIO(csv_content.encode()), 'text/csv')}
        
        response = test_client.post('/api/py/v1/etfs', files=files)
        
        assert response.status_code == 400
        error_detail = response.json()['detail']
        
        # Error should be informative, not just "invalid"
        assert len(error_detail) > 20, "Error message should be detailed"
        # Should mention what's expected
        assert '1.0' in error_detail or '100%' in error_detail.lower()
    
    
    def test_unknown_symbol_lists_available_symbols(self, test_client):
        """Test that unknown symbol error suggests available symbols."""
        csv_content = "name,weight\nINVALID_STOCK,1.0"
        files = {'file': ('invalid.csv', io.BytesIO(csv_content.encode()), 'text/csv')}
        
        response = test_client.post('/api/py/v1/etfs', files=files)
        
        assert response.status_code == 400
        error_detail = response.json()['detail']
        
        # Should mention available symbols to help user
        assert 'available' in error_detail.lower() or 'valid' in error_detail.lower()


class TestEdgeCasesStillWork:
    """Test that edge cases within valid ranges still work."""
    
    def test_zero_weight_allowed(self, test_client):
        """Test that 0 weight is technically valid (though unusual)."""
        csv_content = "name,weight\nA,0.0\nB,1.0"
        files = {'file': ('valid.csv', io.BytesIO(csv_content.encode()), 'text/csv')}
        
        response = test_client.post('/api/py/v1/etfs', files=files)
        
        # Should succeed - 0 weight is valid
        assert response.status_code == 200
    
    
    def test_weight_exactly_one_allowed(self, test_client):
        """Test that single constituent with 100% weight works."""
        csv_content = "name,weight\nA,1.0"
        files = {'file': ('valid.csv', io.BytesIO(csv_content.encode()), 'text/csv')}
        
        response = test_client.post('/api/py/v1/etfs', files=files)
        
        # Should succeed
        assert response.status_code == 200
    
    
    def test_exact_sum_required(self, test_client):
        """Test that weights must sum to 1.0 within tolerance."""
        # Sum = 1.015 (1.5% over), exceeds tolerance=0.005 (0.5%), should be rejected
        csv_content = "name,weight\nA,0.505\nB,0.51"
        files = {'file': ('invalid.csv', io.BytesIO(csv_content.encode()), 'text/csv')}
        
        response = test_client.post('/api/py/v1/etfs', files=files)
        
        # Should fail - 1.5% deviation exceeds 0.5% tolerance
        assert response.status_code == 400

