"""
Services Package

This package contains business logic services for ETF calculations and data loading.

Available services:
- ETFCalculator: Handles ETF price calculations and analytics
- DataLoader: Manages historical price data loading and caching
- ETFValidator: Validates ETF data quality and constraints
"""

# Import services for easier access
from .calculator import ETFCalculator
from .data_loader import DataLoader
from .validator import ETFValidator

# Define what gets imported with "from api.services import *"
__all__ = ['ETFCalculator', 'DataLoader', 'ETFValidator']

