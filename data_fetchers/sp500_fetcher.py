import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import logging
from config.settings import DAYS_OF_HISTORY
from utils.cache_manager import CacheManager

cache = CacheManager()

def get_sp500_data():
    """Fetch S&P 500 historical data"""
    try:
        # Try to get from cache first (cache for 1 hour)
        cached_data = cache.get('sp500', max_age_minutes=60)
        if cached_data is not None:
            data = pd.Series(
                data=cached_data['values'],
                index=pd.to_datetime(cached_data['index'])
            )
            if len(data) > 2:  # Only use cache if we have more than 2 data points
                logging.info(f"Retrieved {len(data)} S&P 500 data points from cache")
                return data
        
        # Use dynamic date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=DAYS_OF_HISTORY)
        
        logging.info(f"Fetching S&P 500 data from {start_date.date()} to {end_date.date()}")
        
        # Download data using Ticker
        sp500 = yf.Ticker('^GSPC')
        df = sp500.history(start=start_date, end=end_date)
        
        if df.empty or len(df) <= 2:
            logging.error(f"Insufficient S&P 500 data received from yfinance: {len(df) if not df.empty else 0} points")
            return None
            
        # Convert timezone-aware dates to timezone-naive UTC dates
        df.index = df.index.tz_convert('UTC').tz_localize(None)
        close_prices = pd.Series(df['Close'].values, index=df.index)
        close_prices = close_prices.sort_index()
        
        logging.info(f"Data range from {close_prices.index.min()} to {close_prices.index.max()}")
        logging.info(f"Index timezone info: {close_prices.index.tz}")
        
        # Cache the results
        cache_data = {
            'index': close_prices.index.strftime('%Y-%m-%d %H:%M:%S').tolist(),
            'values': close_prices.values.tolist()
        }
        cache.set('sp500', cache_data)
        
        logging.info(f"Successfully fetched {len(close_prices)} S&P 500 data points")
        return close_prices
        
    except Exception as e:
        logging.error(f"Error fetching S&P 500 data: {str(e)}")
        return None