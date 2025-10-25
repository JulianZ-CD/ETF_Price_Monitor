"""
Configuration settings for the ETF Price Monitor API.

Loads settings from environment variables with sensible defaults.
Can be configured via .env file or system environment variables.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# ETF Validation Settings
ETF_WEIGHT_TOLERANCE = float(os.getenv('ETF_WEIGHT_TOLERANCE', '0.005'))
"""
Acceptable deviation for ETF constituent weight sum from 1.0.
Default: 0.005 (0.5%) to handle floating-point precision issues.
"""

