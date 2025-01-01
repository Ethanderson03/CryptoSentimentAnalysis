import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import logging
from config.settings import DAYS_OF_HISTORY
from utils.cache_manager import CacheManager

cache = CacheManager()

def get_vix_data():
    """Fetch VIX historical data"""
    try:
        # Try to get from cache first (cache for 1 hour)
        cached_data = cache.get('vix', max_age_minutes=60)
        if cached_data is not None:
            data = pd.Series(
                data=cached_data['values'],
                index=pd.to_datetime(cached_data['index'])
            )
            if len(data) > 2:  # Only use cache if we have more than 2 data points
                logging.info(f"Retrieved {len(data)} VIX data points from cache")
                return data
        
        # Use dynamic date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=DAYS_OF_HISTORY)
        
        logging.info(f"Fetching VIX data from {start_date.date()} to {end_date.date()}")
        
        # Download data using Ticker
        vix = yf.Ticker('^VIX')
        df = vix.history(start=start_date, end=end_date)
        
        if df.empty or len(df) <= 2:
            logging.error(f"Insufficient VIX data received from yfinance: {len(df) if not df.empty else 0} points")
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
        cache.set('vix', cache_data)
        
        logging.info(f"Successfully fetched {len(close_prices)} VIX data points")
        return close_prices
        
    except Exception as e:
        logging.error(f"Error fetching VIX data: {str(e)}")
        return None 