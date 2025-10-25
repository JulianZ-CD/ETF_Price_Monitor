"""
Unit Tests for ETFValidator Service

Tests data validation logic including edge cases and error conditions.
"""

from api.services import ETFValidator


class TestWeightSumValidation:
    """Test weight sum validation."""
    
    def test_valid_weight_sum_exactly_one(self):
        """Test that weights summing to exactly 1.0 pass validation."""
        validator = ETFValidator(tolerance=0.0)  # Strict: must be exactly 1.0
        constituents = [
            {'name': 'A', 'weight': 0.5},
            {'name': 'B', 'weight': 0.3},
            {'name': 'C', 'weight': 0.2}  # Sum = 1.0 exactly
        ]
        
        is_valid, error_msg = validator.validate_weights_sum(constituents)
        
        assert is_valid, f"Should be valid but got error: {error_msg}"
        assert error_msg == ""
    
    
    def test_valid_weight_sum_within_tolerance(self):
        """Test that weights within tolerance pass validation."""
        validator = ETFValidator(tolerance=0.01)  # Set tolerance to 0.01 for this test
        constituents = [
            {'name': 'A', 'weight': 0.5},
            {'name': 'B', 'weight': 0.3},
            {'name': 'C', 'weight': 0.205}  # Sum = 1.005, within 1% tolerance
        ]
        
        is_valid, error_msg = validator.validate_weights_sum(constituents)
        
        assert is_valid, "Should pass with 0.5% deviation when tolerance=0.01"
    
    
    def test_invalid_weight_sum_too_low(self):
        """Test that weights summing to less than 1.0 fail validation."""
        validator = ETFValidator(tolerance=0.0)  # Strict: must be exactly 1.0
        constituents = [
            {'name': 'A', 'weight': 0.5},
            {'name': 'B', 'weight': 0.3}  # Sum = 0.8, missing 20%!
        ]
        
        is_valid, error_msg = validator.validate_weights_sum(constituents)
        
        assert not is_valid, "Should fail with 80% total"
        assert "0.8" in error_msg or "0.80" in error_msg
        assert "1.0" in error_msg
    
    
    def test_invalid_weight_sum_too_high(self):
        """Test that weights summing to more than 1.0 fail validation."""
        validator = ETFValidator(tolerance=0.0)  # Strict: must be exactly 1.0
        constituents = [
            {'name': 'A', 'weight': 0.5},
            {'name': 'B', 'weight': 0.51}  # Sum = 1.01, 101%!
        ]
        
        is_valid, error_msg = validator.validate_weights_sum(constituents)
        
        assert not is_valid, "Should fail with 110% total"
        assert "1.01" in error_msg


class TestWeightRangeValidation:
    """Test individual weight range validation."""
    
    def test_valid_weight_ranges(self):
        """Test that weights between 0 and 1 pass validation."""
        validator = ETFValidator()
        constituents = [
            {'name': 'A', 'weight': 0.0},   # Edge: 0%
            {'name': 'B', 'weight': 0.5},
            {'name': 'C', 'weight': 1.0}    # Edge: 100%
        ]
        
        is_valid, error_msg = validator.validate_weight_ranges(constituents)
        
        assert is_valid
        assert error_msg == ""
    
    
    def test_invalid_negative_weight(self):
        """Test that negative weights fail validation."""
        validator = ETFValidator()
        constituents = [
            {'name': 'A', 'weight': 0.5},
            {'name': 'B', 'weight': -0.2}  # ❌ Negative!
        ]
        
        is_valid, error_msg = validator.validate_weight_ranges(constituents)
        
        assert not is_valid
        assert 'B' in error_msg
        assert 'negative' in error_msg.lower()
    
    
    def test_invalid_weight_above_one(self):
        """Test that weights > 1.0 fail validation."""
        validator = ETFValidator()
        constituents = [
            {'name': 'A', 'weight': 1.5}  # ❌ More than 100%!
        ]
        
        is_valid, error_msg = validator.validate_weight_ranges(constituents)
        
        assert not is_valid
        assert 'A' in error_msg
        assert '1.5' in error_msg
    
    
    def test_multiple_invalid_weights(self):
        """Test error message contains all invalid weights."""
        validator = ETFValidator()
        constituents = [
            {'name': 'A', 'weight': -0.1},  # ❌ Negative
            {'name': 'B', 'weight': 0.5},   # ✅ OK
            {'name': 'C', 'weight': 1.2}    # ❌ Too high
        ]
        
        is_valid, error_msg = validator.validate_weight_ranges(constituents)
        
        assert not is_valid
        # Should mention both A and C
        assert 'A' in error_msg
        assert 'C' in error_msg
        # Should NOT mention B (it's valid)
        assert 'B' not in error_msg or 'B:' not in error_msg


class TestSymbolExistenceValidation:
    """Test symbol existence validation."""
    
    def test_all_symbols_exist(self):
        """Test that validation passes when all symbols exist."""
        validator = ETFValidator()
        constituents = [
            {'name': 'A', 'weight': 0.5},
            {'name': 'B', 'weight': 0.5}
        ]
        available_symbols = ['A', 'B', 'C', 'D']
        
        is_valid, error_msg, missing = validator.validate_symbols_exist(
            constituents, available_symbols
        )
        
        assert is_valid
        assert error_msg == ""
        assert len(missing) == 0
    
    
    def test_missing_single_symbol(self):
        """Test that validation fails for missing symbol."""
        validator = ETFValidator()
        constituents = [
            {'name': 'A', 'weight': 0.5},
            {'name': 'UNKNOWN', 'weight': 0.5}  # ❌ Doesn't exist
        ]
        available_symbols = ['A', 'B', 'C']
        
        is_valid, error_msg, missing = validator.validate_symbols_exist(
            constituents, available_symbols
        )
        
        assert not is_valid
        assert 'UNKNOWN' in error_msg
        assert missing == ['UNKNOWN']
    
    
    def test_multiple_missing_symbols(self):
        """Test error message lists all missing symbols."""
        validator = ETFValidator()
        constituents = [
            {'name': 'A', 'weight': 0.3},
            {'name': 'MISSING1', 'weight': 0.3},  # ❌
            {'name': 'MISSING2', 'weight': 0.4}   # ❌
        ]
        available_symbols = ['A', 'B', 'C']
        
        is_valid, error_msg, missing = validator.validate_symbols_exist(
            constituents, available_symbols
        )
        
        assert not is_valid
        assert 'MISSING1' in error_msg
        assert 'MISSING2' in error_msg
        assert len(missing) == 2


class TestNonEmptyValidation:
    """Test non-empty constituents validation."""
    
    def test_valid_non_empty_list(self):
        """Test that non-empty list passes validation."""
        validator = ETFValidator()
        constituents = [{'name': 'A', 'weight': 1.0}]
        
        is_valid, error_msg = validator.validate_non_empty(constituents)
        
        assert is_valid
        assert error_msg == ""
    
    
    def test_invalid_empty_list(self):
        """Test that empty list fails validation."""
        validator = ETFValidator()
        constituents = []
        
        is_valid, error_msg = validator.validate_non_empty(constituents)
        
        assert not is_valid
        assert 'at least one' in error_msg.lower()


class TestValidateAll:
    """Test comprehensive validation."""
    
    def test_all_validations_pass(self):
        """Test that valid data passes all checks."""
        validator = ETFValidator(tolerance=0.0)  # Strict validation
        constituents = [
            {'name': 'A', 'weight': 0.6},
            {'name': 'B', 'weight': 0.4}  # Sum = 1.0 exactly
        ]
        available_symbols = ['A', 'B', 'C']
        
        is_valid, errors = validator.validate_all(constituents, available_symbols)
        
        assert is_valid
        assert len(errors) == 0
    
    
    def test_multiple_validation_failures(self):
        """Test that multiple errors are collected."""
        validator = ETFValidator(tolerance=0.0)  # Strict validation
        constituents = [
            {'name': 'A', 'weight': -0.2},      # ❌ Negative weight
            {'name': 'UNKNOWN', 'weight': 0.5}  # ❌ Unknown symbol
            # Sum = 0.3 ❌ Not 1.0
        ]
        available_symbols = ['A', 'B', 'C']
        
        is_valid, errors = validator.validate_all(constituents, available_symbols)
        
        assert not is_valid
        assert len(errors) >= 2  # Should have at least 2 errors
        # Check that errors cover different issues
        error_text = '\n'.join(errors)
        assert 'negative' in error_text.lower() or 'range' in error_text.lower()
        assert 'UNKNOWN' in error_text or 'symbol' in error_text.lower()
    
    
    def test_empty_constituents_stops_validation(self):
        """Test that empty list stops further validation."""
        validator = ETFValidator()
        constituents = []
        available_symbols = ['A', 'B']
        
        is_valid, errors = validator.validate_all(constituents, available_symbols)
        
        assert not is_valid
        assert len(errors) == 1  # Only empty error, no further checks
        assert 'at least one' in errors[0].lower()


class TestToleranceConfiguration:
    """Test validator tolerance configuration."""
    
    def test_strict_tolerance(self):
        """Test with very strict tolerance."""
        validator = ETFValidator(tolerance=0.001)  # 0.1% tolerance
        constituents = [
            {'name': 'A', 'weight': 0.505},
            {'name': 'B', 'weight': 0.500}  # Sum = 1.005
        ]
        
        is_valid, _ = validator.validate_weights_sum(constituents)
        
        # 1.005 is > 1.001, so should fail with strict tolerance
        assert not is_valid
    
    
    def test_loose_tolerance(self):
        """Test with loose tolerance."""
        validator = ETFValidator(tolerance=0.05)  # 5% tolerance
        constituents = [
            {'name': 'A', 'weight': 0.505},
            {'name': 'B', 'weight': 0.500}  # Sum = 1.005
        ]
        
        is_valid, _ = validator.validate_weights_sum(constituents)
        
        # 1.005 is within 5% tolerance
        assert is_valid

