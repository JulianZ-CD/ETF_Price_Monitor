"""
ETF data parser service.
Handles CSV parsing and format validation (not business rules).
"""

import pandas as pd
import io
from typing import List, Dict, Any
from api.utils.logger import setup_logger

logger = setup_logger(__name__)


class ETFDataParser:
    """
    Parses and validates ETF data format.
    
    Responsibilities:
    - Parse CSV files
    - Validate file format (columns, data types)
    - Transform data to standard structure
    
    Does NOT validate business rules (use ETFValidator for that).
    """
    
    def parse_csv_file(self, content: bytes, filename: str = "uploaded_file") -> List[Dict[str, Any]]:
        """
        Parse CSV file content and return standardized constituent data.
        
        This method handles:
        1. CSV parsing
        2. Column validation (name, weight)
        3. Data type conversion (weight to float)
        
        Args:
            content: Raw file content in bytes
            filename: Name of the file (for logging)
            
        Returns:
            List of dicts with 'name' and 'weight' keys
            
        Raises:
            ValueError: If file format is invalid
        """
        logger.info(f"Parsing ETF file: {filename} ({len(content)} bytes)")
        
        # Step 1: Parse CSV
        try:
            df = pd.read_csv(io.StringIO(content.decode('utf-8')))
            logger.debug(f"CSV parsed successfully: {len(df)} rows, {len(df.columns)} columns")
        except Exception as e:
            logger.error(f"Failed to parse CSV: {str(e)}")
            raise ValueError(f"Invalid CSV format: {str(e)}")
        
        # Step 2: Validate required columns
        required_columns = {'name', 'weight'}
        actual_columns = set(df.columns)
        
        if not required_columns.issubset(actual_columns):
            missing = required_columns - actual_columns
            logger.warning(f"Missing required columns: {missing}. Found: {list(actual_columns)}")
            raise ValueError(
                f"CSV must contain 'name' and 'weight' columns. "
                f"Found: {list(actual_columns)}"
            )
        
        # Step 3: Check for empty data
        if len(df) == 0:
            logger.warning("CSV file contains no data rows")
            raise ValueError("CSV file is empty")
        
        # Step 4: Convert to list of dicts
        constituents = df[['name', 'weight']].to_dict('records')
        
        # Step 5: Convert weights to float
        try:
            for constituent in constituents:
                constituent['weight'] = float(constituent['weight'])
        except (ValueError, TypeError) as e:
            logger.warning(f"Invalid weight value: {str(e)}")
            raise ValueError(f"All weights must be numeric values. Error: {str(e)}")
        
        logger.info(f"Successfully parsed {len(constituents)} constituents")
        return constituents

