"""
Routers Package

This package contains API route handlers for different resource endpoints.

Available routers:
- etf_router: Handles ETF-related endpoints (upload, analysis)
"""

# Import the etf_router module for access to its router object
from . import etf_router

# Define what gets imported with "from api.routers import *"
__all__ = ['etf_router']

