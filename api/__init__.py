"""
ETF Price Monitor API Package

This package provides a FastAPI-based REST API for analyzing ETF constituents
and calculating historical prices based on weighted constituents.

Modules:
- index: FastAPI application instance
- routers: API route handlers
- services: Business logic and data processing
"""

# Package version
__version__ = "1.0.0"

# Note: The FastAPI app is initialized in index.py
# Import services only (to avoid circular imports with routers)
from .services import ETFCalculator, DataLoader

# Define what gets imported with "from api import *"
__all__ = [
    'ETFCalculator', 
    'DataLoader',
]

