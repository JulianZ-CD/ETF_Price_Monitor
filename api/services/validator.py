"""
Validator service for ETF data validation.
Ensures data quality and provides clear error messages to users.
"""

from typing import List, Dict, Any, Tuple


class ETFValidator:
    """
    Validates ETF constituents data to ensure data quality.
    
    This class performs various checks on ETF data before processing:
    - Weight sum validation (should equal 1.0)
    - Weight range validation (0 to 1)
    - Symbol existence validation
    """
    
    def __init__(self, tolerance: float = 0.0):
        """
        Initialize validator.
        
        Args:
            tolerance: Acceptable deviation for weight sum from 1.0 (default: 0.0, no tolerance)
                      For example, with tolerance=0.02, values from 0.98 to 1.02 are acceptable
        """
        self.tolerance = tolerance
    
    def validate_weights_sum(self, constituents: List[Dict[str, Any]]) -> Tuple[bool, str]:
        """
        Validate that weights sum to approximately 1.0.
        
        Why this matters:
        - ETF weights represent percentages (should total 100%)
        - Incorrect sum indicates data error or incomplete data
        
        Args:
            constituents: List of dicts with 'name' and 'weight' keys
            
        Returns:
            Tuple of (is_valid, error_message)
            - (True, "") if valid
            - (False, "error message") if invalid
        """
        total_weight = sum(c['weight'] for c in constituents)
        
        # Check if within tolerance
        if abs(total_weight - 1.0) > self.tolerance:
            return (
                False,
                f"Weight sum validation failed: weights sum to {total_weight:.4f}, "
                f"expected 1.0 ± {self.tolerance}. "
                f"Please ensure all constituent weights add up to 100%."
            )
        
        return (True, "")
    
    def validate_weight_ranges(self, constituents: List[Dict[str, Any]]) -> Tuple[bool, str]:
        """
        Validate that all weights are in valid range [0, 1].
        
        Why this matters:
        - Negative weights don't make sense in ETF context
        - Weights > 1 would mean more than 100% allocation to one stock
        
        Args:
            constituents: List of dicts with 'name' and 'weight' keys
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        invalid_weights = []
        
        for constituent in constituents:
            weight = constituent['weight']
            symbol = constituent['name']
            
            if weight < 0:
                invalid_weights.append(f"{symbol}: {weight} (negative weight)")
            elif weight > 1:
                invalid_weights.append(f"{symbol}: {weight} (exceeds 100%)")
        
        if invalid_weights:
            return (
                False,
                f"Invalid weight values detected:\n" + "\n".join(f"  - {w}" for w in invalid_weights)
            )
        
        return (True, "")
    
    def validate_symbols_exist(
        self, 
        constituents: List[Dict[str, Any]], 
        available_symbols: List[str]
    ) -> Tuple[bool, str, List[str]]:
        """
        Validate that all constituent symbols exist in price data.
        
        Why this matters:
        - Can't calculate ETF price for stocks we don't have data for
        - User should know immediately if data is missing
        
        Args:
            constituents: List of dicts with 'name' and 'weight' keys
            available_symbols: List of available stock symbols
            
        Returns:
            Tuple of (is_valid, error_message, missing_symbols)
            - is_valid: True if all symbols exist
            - error_message: Description of missing symbols
            - missing_symbols: List of symbols not found
        """
        missing_symbols = []
        
        for constituent in constituents:
            symbol = constituent['name']
            if symbol not in available_symbols:
                missing_symbols.append(symbol)
        
        if missing_symbols:
            return (
                False,
                f"The following symbols were not found in price data: {', '.join(missing_symbols)}. "
                f"Available symbols: {', '.join(sorted(available_symbols)[:10])}...",
                missing_symbols
            )
        
        return (True, "", [])
    
    def validate_non_empty(self, constituents: List[Dict[str, Any]]) -> Tuple[bool, str]:
        """
        Validate that constituents list is not empty.
        
        Args:
            constituents: List of constituents
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not constituents or len(constituents) == 0:
            return (False, "ETF must have at least one constituent")
        
        return (True, "")
    
    def validate_no_duplicates(self, constituents: List[Dict[str, Any]]) -> Tuple[bool, str]:
        """
        Validate that there are no duplicate symbols.
        
        Why this matters:
        - Duplicate symbols lead to incorrect weight calculations
        - Each constituent should appear only once
        
        Args:
            constituents: List of dicts with 'name' key
            
        Returns:
            Tuple of (is_valid, error_message)
            - (True, "") if no duplicates
            - (False, "error message") if duplicates found
        """
        symbols = [c['name'] for c in constituents]
        seen = set()
        duplicates = set()
        
        for symbol in symbols:
            if symbol in seen:
                duplicates.add(symbol)
            seen.add(symbol)
        
        if duplicates:
            dup_list = sorted(list(duplicates))
            return (
                False,
                f"Duplicate symbols found: {', '.join(dup_list)}"
            )
        
        return (True, "")
    
    def validate_all(
        self, 
        constituents: List[Dict[str, Any]], 
        available_symbols: List[str]
    ) -> Tuple[bool, List[str]]:
        """
        Run all validations and collect errors.
        
        This is a convenience method that runs all validation checks
        and returns a comprehensive list of all errors found.
        
        Args:
            constituents: List of dicts with 'name' and 'weight' keys
            available_symbols: List of available stock symbols
            
        Returns:
            Tuple of (is_valid, error_messages)
            - is_valid: True only if ALL validations pass
            - error_messages: List of all error messages (empty if valid)
            
        Example:
            is_valid, errors = validator.validate_all(constituents, symbols)
            if not is_valid:
                raise ValueError("\\n".join(errors))
        """
        errors = []
        
        # Check 1: Non-empty
        valid, msg = self.validate_non_empty(constituents)
        if not valid:
            errors.append(msg)
            return (False, errors)  # No point continuing if empty
        
        # Check 2: No duplicates
        valid, msg = self.validate_no_duplicates(constituents)
        if not valid:
            errors.append(msg)
        
        # Check 3: Weight ranges
        valid, msg = self.validate_weight_ranges(constituents)
        if not valid:
            errors.append(msg)
        
        # Check 4: Weight sum
        valid, msg = self.validate_weights_sum(constituents)
        if not valid:
            errors.append(msg)
        
        # Check 5: Symbol existence
        valid, msg, _ = self.validate_symbols_exist(constituents, available_symbols)
        if not valid:
            errors.append(msg)
        
        return (len(errors) == 0, errors)

