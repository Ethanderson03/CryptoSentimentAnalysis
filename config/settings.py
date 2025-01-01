"""
Global configuration settings for the CMS application.
"""
import os

# Data fetching settings
DAYS_OF_HISTORY = 365  # Number of days of historical data to fetch
TOP_N_CRYPTO = 50     # Number of top cryptocurrencies to analyze

# API Configuration
CMC_API_KEY = os.getenv('CMC_API_KEY')  # Get CoinMarketCap API key from environment
CMC_BASE_URL = "https://pro-api.coinmarketcap.com/v1"
FEAR_GREED_URL = "https://api.alternative.me/fng/?limit=0"  # Fear & Greed Index API

# Cache settings
CACHE_DIR = ".cache"  # Directory to store cache files 