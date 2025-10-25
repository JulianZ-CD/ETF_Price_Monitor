"""
ETF router handling all ETF-related endpoints.
This module contains endpoints for uploading ETF files and retrieving ETF data.
"""

from fastapi import APIRouter, File, UploadFile, HTTPException
from typing import Dict, Any
from api.services import DataLoader, ETFCalculator, ETFValidator, ETFDataParser
from api.utils.config import ETF_WEIGHT_TOLERANCE
from api.utils.logger import setup_logger

logger = setup_logger(__name__)

# Create router instance with API versioning

router = APIRouter(prefix="/api/py/v1", tags=["ETF"])

# Initialize services
data_loader = DataLoader()
calculator = ETFCalculator()
validator = ETFValidator(tolerance=ETF_WEIGHT_TOLERANCE)
parser = ETFDataParser()


@router.post("/etfs")
async def create_etf_analysis(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Create ETF analysis from uploaded CSV file.
    
    Expected CSV format:
    name,weight
    A,0.02
    B,0.15
    ...
    
    Returns:
        Dict containing table_data, time_series, and top_holdings
    """
    try:
        # Step 1: Parse and validate file format
        content = await file.read()
        try:
            constituents = parser.parse_csv_file(content, file.filename)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        # Step 2: Validate business rules
        available_symbols = data_loader.get_available_symbols()
        is_valid, errors = validator.validate_all(constituents, available_symbols)
        
        if not is_valid:
            logger.warning(f"ETF validation failed with {len(errors)} error(s): {errors}")
            error_detail = "ETF data validation failed:\n" + "\n".join(f"- {err}" for err in errors)
            raise HTTPException(status_code=400, detail=error_detail)
        
        # Step 3: Calculate ETF data
        # Get table data (constituents with latest prices)
        table_data = calculator.get_latest_prices(constituents)
        
        # Calculate time series (historical ETF prices)
        etf_prices_df = calculator.calculate_etf_prices(constituents)
        time_series = [
            {
                'date': row['DATE'].strftime('%Y-%m-%d'),
                'price': float(row['etf_price'])
            }
            for _, row in etf_prices_df.iterrows()
        ]
        
        # Calculate top 5 holdings
        top_holdings = calculator.get_top_holdings(constituents, top_n=5)
        
        logger.info(f"ETF analysis completed: {len(constituents)} constituents, {len(time_series)} data points")
        
        return {
            'status': 'success',
            'table_data': table_data,
            'time_series': time_series,
            'top_holdings': top_holdings
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in ETF analysis: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/health")
def health_check():
    """
    Health check endpoint to verify the API is running and data is loaded.
    """
    return {
        'status': 'healthy',
        'service': 'etf-api',
        'version': 'v1',
        'data_loaded': data_loader._prices_df is not None
    }

