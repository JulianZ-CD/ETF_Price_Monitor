"""
Configuration settings for the ETF Price Monitor API.

Loads settings from environment variables with sensible defaults.
Can be configured via .env file or system environment variables.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from api.utils import setup_logger

# Setup logger
logger = setup_logger(__name__)

# Determine which .env file to load
# Priority: ENV_FILE env var > .env.dev > .env.prod > .env
env_file = os.getenv('ENV_FILE')
if env_file:
    env_path = Path(env_file)
else:
    # Try in order: .env.dev, .env.prod, .env
    base_dir = Path(__file__).resolve().parent.parent
    for filename in ['.env.dev', '.env.prod', '.env']:
        env_path = base_dir / filename
        if env_path.exists():
            break
    else:
        env_path = None

# Load environment variables
if env_path and env_path.exists():
    load_dotenv(env_path)
    logger.info(f"Loaded configuration from: {env_path.name}")
else:
    logger.info("Using system environment variables (no .env file found)")

# ETF Validation Settings
ETF_WEIGHT_TOLERANCE = float(os.getenv('ETF_WEIGHT_TOLERANCE', '0.005'))
logger.info(f"ETF_WEIGHT_TOLERANCE = {ETF_WEIGHT_TOLERANCE} ({ETF_WEIGHT_TOLERANCE * 100}%)")

"""
Acceptable deviation for ETF constituent weight sum from 1.0.
Default: 0.005 (0.5%) to handle floating-point precision issues.
"""

