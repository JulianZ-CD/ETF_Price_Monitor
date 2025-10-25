"""
ETF router handling all ETF-related endpoints.
This module contains endpoints for uploading ETF files and retrieving ETF data.
"""

from fastapi import APIRouter, File, UploadFile, HTTPException
import pandas as pd
import io
from typing import Dict, Any
from api.services import DataLoader, ETFCalculator, ETFValidator

# Create router instance with API versioning

router = APIRouter(prefix="/api/py/v1", tags=["ETF"])

# Initialize services
data_loader = DataLoader()
calculator = ETFCalculator()
validator = ETFValidator(tolerance=0.005)  # Allow ±0.5% deviation for rounding and float precision


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
        # Read the uploaded file
        contents = await file.read()
        
        # Parse CSV file
        try:
            etf_df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid CSV format: {str(e)}")
        
        # Validate required columns
        if 'name' not in etf_df.columns or 'weight' not in etf_df.columns:
            raise HTTPException(
                status_code=400, 
                detail="CSV must contain 'name' and 'weight' columns"
            )
        
        # Convert DataFrame to list of dicts
        constituents = etf_df.to_dict('records')
        
        # Validate that weights are numeric
        try:
            for constituent in constituents:
                constituent['weight'] = float(constituent['weight'])
        except (ValueError, TypeError):
            raise HTTPException(status_code=400, detail="Weights must be numeric values")
        
        # Validate ETF data quality
        available_symbols = data_loader.get_available_symbols()
        is_valid, errors = validator.validate_all(constituents, available_symbols)
        
        if not is_valid:
            # Return user-friendly error message with all issues
            error_detail = "ETF data validation failed:\n" + "\n".join(f"- {err}" for err in errors)
            raise HTTPException(status_code=400, detail=error_detail)
        
        # Calculate ETF data
        # 1. Get table data (constituents with latest prices)
        table_data = calculator.get_latest_prices(constituents)
        
        # 2. Calculate time series (historical ETF prices)
        etf_prices_df = calculator.calculate_etf_prices(constituents)
        time_series = [
            {
                'date': row['DATE'].strftime('%Y-%m-%d'),
                'price': float(row['etf_price'])
            }
            for _, row in etf_prices_df.iterrows()
        ]
        
        # 3. Calculate top 5 holdings
        top_holdings = calculator.get_top_holdings(constituents, top_n=5)
        
        return {
            'status': 'success',
            'table_data': table_data,
            'time_series': time_series,
            'top_holdings': top_holdings
        }
        
    except HTTPException:
        raise
    except Exception as e:
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

