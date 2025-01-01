import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys
CMC_API_KEY = os.getenv('CMC_API_KEY')

# API URLs
CMC_BASE_URL = os.getenv('CMC_BASE_URL', 'https://pro-api.coinmarketcap.com/v1')
FEAR_GREED_URL = os.getenv('FEAR_GREED_URL', 'https://api.alternative.me/fng/')

# Data settings
DAYS_OF_HISTORY = int(os.getenv('DAYS_OF_HISTORY', '365'))
TOP_N_CRYPTO = int(os.getenv('TOP_N_CRYPTO', '50'))

# Visualization settings
PLOT_HEIGHT = int(os.getenv('PLOT_HEIGHT', '1200')) 