import requests
import pandas as pd
from config.settings import FEAR_GREED_URL
from utils.cache_manager import CacheManager
import logging

cache = CacheManager()

def get_crypto_fear_greed():
    """Fetch Crypto Fear & Greed Index data"""
    # Try to get from cache first (cache for 1 hour)
    cached_data = cache.get('fear_greed', max_age_minutes=60)
    if cached_data is not None:
        return pd.Series(data=cached_data['values'], index=pd.to_datetime(cached_data['index']))
    
    try:
        url = FEAR_GREED_URL
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        # Create DataFrame from the data
        records = []
        for item in data['data']:
            records.append({
                'timestamp': pd.to_datetime(int(item['timestamp']), unit='s'),
                'value': float(item['value'])
            })
        
        df = pd.DataFrame.from_records(records)
        df.set_index('timestamp', inplace=True)
        df = df.sort_index()
        
        # Prepare data for caching
        cache_data = {
            'index': df.index.strftime('%Y-%m-%d %H:%M:%S').tolist(),
            'values': df['value'].tolist()
        }
        
        # Cache the results
        cache.set('fear_greed', cache_data)
        
        return df['value']
        
    except Exception as e:
        logging.error(f"Error fetching Fear & Greed data: {str(e)}")
        return None 