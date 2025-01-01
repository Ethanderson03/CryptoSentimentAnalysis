import json
import os
import pandas as pd
from datetime import datetime, timedelta
import logging

class CacheManager:
    def __init__(self, cache_dir=".cache"):
        self.cache_dir = cache_dir
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
    
    def get(self, key, max_age_minutes=None):
        """Get data from cache if it exists and is not expired"""
        cache_file = os.path.join(self.cache_dir, f"{key}.json")
        if not os.path.exists(cache_file):
            return None
        
        try:
            with open(cache_file, 'r') as f:
                cached = json.load(f)
            
            if max_age_minutes is not None:
                cache_time = datetime.fromisoformat(cached['timestamp'])
                if datetime.now() - cache_time > timedelta(minutes=max_age_minutes):
                    return None
            
            return cached['data']
        except Exception as e:
            logging.error(f"Error reading cache file {cache_file}: {str(e)}")
            return None
    
    def set(self, key, data):
        """Save data to cache"""
        cache_file = os.path.join(self.cache_dir, f"{key}.json")
        try:
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'data': data
            }
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f)
        except Exception as e:
            logging.error(f"Error writing to cache file {cache_file}: {str(e)}")
    
    def clear_all(self):
        """Clear all cached data"""
        try:
            for file in os.listdir(self.cache_dir):
                if file.endswith('.json'):
                    os.remove(os.path.join(self.cache_dir, file))
            logging.info("Cache cleared successfully")
        except Exception as e:
            logging.error(f"Error clearing cache: {str(e)}")
    
    def delete(self, key):
        """Delete a specific cache entry"""
        cache_file = os.path.join(self.cache_dir, f"{key}.json")
        try:
            if os.path.exists(cache_file):
                os.remove(cache_file)
                logging.info(f"Cache entry {key} deleted successfully")
        except Exception as e:
            logging.error(f"Error deleting cache entry {key}: {str(e)}") 