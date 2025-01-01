import json
import os
import pandas as pd
from datetime import datetime, timedelta

class CacheManager:
    def __init__(self, cache_dir='cache'):
        self.cache_dir = cache_dir
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
    
    def _get_cache_path(self, key):
        return os.path.join(self.cache_dir, f"{key}.json")
    
    def get(self, key, max_age_minutes=None):
        """Get data from cache if it exists and is not expired"""
        cache_path = self._get_cache_path(key)
        if not os.path.exists(cache_path):
            return None
        
        try:
            with open(cache_path, 'r') as f:
                cache_data = json.load(f)
            
            if max_age_minutes is not None:
                cache_time = datetime.fromisoformat(cache_data['timestamp'])
                if datetime.now() - cache_time > timedelta(minutes=max_age_minutes):
                    return None
            
            return cache_data['data']
        except:
            return None
    
    def set(self, key, data):
        """Save data to cache with current timestamp"""
        cache_path = self._get_cache_path(key)
        try:
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'data': data
            }
            with open(cache_path, 'w') as f:
                json.dump(cache_data, f)
        except:
            pass  # Silently fail if we can't cache
    
    def clear(self, key):
        """Clear specific cache entry"""
        cache_path = self._get_cache_path(key)
        if os.path.exists(cache_path):
            try:
                os.remove(cache_path)
            except:
                pass
    
    def clear_all(self):
        """Clear all cache entries"""
        try:
            for file in os.listdir(self.cache_dir):
                if file.endswith('.json'):
                    os.remove(os.path.join(self.cache_dir, file))
        except:
            pass 