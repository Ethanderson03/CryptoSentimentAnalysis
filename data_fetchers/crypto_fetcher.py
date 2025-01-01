import requests
import pandas as pd
from datetime import datetime, timedelta
from config.settings import CMC_API_KEY, CMC_BASE_URL, TOP_N_CRYPTO, DAYS_OF_HISTORY
from utils.cache_manager import CacheManager
import logging
import time

cache = CacheManager()

def get_top_crypto_data():
    """Fetch current top N cryptocurrencies data from CoinMarketCap"""
    # Try to get from cache first (cache for 5 minutes)
    cached_data = cache.get('crypto_prices', max_age_minutes=5)
    if cached_data is not None:
        logging.info(f"Retrieved top {len(cached_data)} cryptocurrencies from cache")
        return pd.Series(cached_data)
    
    # If not in cache, fetch from API
    logging.info(f"Fetching top {TOP_N_CRYPTO} cryptocurrencies from CoinMarketCap")
    url = f'{CMC_BASE_URL}/cryptocurrency/listings/latest'
    headers = {
        'X-CMC_PRO_API_KEY': CMC_API_KEY,
        'Accept': 'application/json'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an error for bad status codes
        data = response.json()
        
        crypto_data = {}
        for coin in data['data'][:TOP_N_CRYPTO]:
            crypto_data[coin['symbol']] = {
                'price': coin['quote']['USD']['price'],
                'id': coin['id']
            }
        
        # Cache the results
        cache.set('crypto_prices', crypto_data)
        logging.info(f"Successfully fetched and cached {len(crypto_data)} cryptocurrencies")
        
        return pd.Series({k: v['price'] for k, v in crypto_data.items()})
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching data from CoinMarketCap: {str(e)}")
        return pd.Series()

def get_historical_crypto_data(symbol):
    """Fetch historical data for a specific cryptocurrency"""
    # Try to get from cache first
    cache_key = f'crypto_historical_{symbol}'
    cached_data = cache.get(cache_key)
    
    if cached_data is not None and cached_data.get('data', {}).get('price', []):
        logging.info(f"Retrieved historical data for {symbol} from cache")
        # Convert cached data to DataFrame
        data = cached_data['data']
        index = pd.to_datetime(cached_data['index'])
        return pd.DataFrame(data, index=index)
    
    # If not in cache or invalid cache, fetch from API
    logging.info(f"Fetching historical data for {symbol} from API")
    end_date = datetime.now()
    start_date = end_date - timedelta(days=DAYS_OF_HISTORY)
    
    # Try CMC first
    try:
        # Get the CMC ID for this symbol
        top_cryptos = get_top_crypto_data()
        if symbol not in top_cryptos.index:
            logging.warning(f"No CMC ID found for {symbol}, falling back to yfinance")
            raise ValueError(f"Symbol {symbol} not found in CMC data")
        
        # Fetch historical data from CMC
        url = f'{CMC_BASE_URL}/cryptocurrency/ohlcv/historical'
        params = {
            'symbol': symbol,
            'time_start': start_date.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'time_end': end_date.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'interval': '1d',  # Daily data
            'convert': 'USD'
        }
        headers = {
            'X-CMC_PRO_API_KEY': CMC_API_KEY,
            'Accept': 'application/json'
        }
        
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Process CMC data
        quotes = data['data']['quotes']
        dates = []
        prices = []
        market_caps = []
        
        for quote in quotes:
            dates.append(pd.to_datetime(quote['time_open']))
            prices.append(quote['quote']['USD']['close'])
            market_caps.append(quote['quote']['USD']['market_cap'])
        
        # Create DataFrame
        df = pd.DataFrame({
            'price': prices,
            'market_cap': market_caps
        }, index=pd.DatetimeIndex(dates))
        
        # Convert timezone-aware index to timezone-naive UTC
        if df.index.tz is not None:
            df.index = df.index.tz_convert('UTC').tz_localize(None)
        
        if df.empty:
            logging.warning(f"No data returned from CMC for {symbol}")
            raise ValueError("Empty dataset from CMC")
        
        # Prepare data for caching
        cache_data = {
            'data': {
                'price': df['price'].tolist(),
                'market_cap': df['market_cap'].tolist()
            },
            'index': df.index.strftime('%Y-%m-%d %H:%M:%S').tolist()
        }
        cache.set(cache_key, cache_data)
        logging.info(f"Successfully fetched and cached CMC data for {symbol}")
        
        return df
        
    except Exception as e:
        logging.warning(f"Failed to fetch CMC data for {symbol}, falling back to yfinance: {str(e)}")
        
        # Fallback to yfinance
        try:
            import yfinance as yf
            ticker = yf.Ticker(f"{symbol}-USD")
            df = ticker.history(start=start_date, end=end_date)
            
            if df.empty:
                logging.warning(f"No data returned from yfinance for {symbol}")
                return pd.DataFrame()
            
            # Convert timezone-aware index to timezone-naive UTC
            if df.index.tz is not None:
                df.index = df.index.tz_convert('UTC').tz_localize(None)
            
            # Prepare data for caching
            cache_data = {
                'data': {
                    'price': df['Close'].tolist(),
                    'market_cap': (df['Close'] * df['Volume']).tolist()
                },
                'index': df.index.strftime('%Y-%m-%d %H:%M:%S').tolist()
            }
            cache.set(cache_key, cache_data)
            logging.info(f"Successfully fetched and cached yfinance data for {symbol}")
            
            # Return processed DataFrame
            return pd.DataFrame({
                'price': df['Close'],
                'market_cap': df['Close'] * df['Volume']
            }, index=df.index)
        except Exception as e:
            logging.error(f"Error fetching data for {symbol}: {str(e)}")
            return pd.DataFrame()

def get_all_historical_data():
    """Fetch historical data for all top cryptocurrencies"""
    # Get current top N crypto list
    top_cryptos = get_top_crypto_data()
    if top_cryptos.empty:
        logging.error("Failed to get list of top cryptocurrencies")
        return {}
    
    symbols = top_cryptos.index.tolist()
    logging.info(f"Available coins: {', '.join(sorted(symbols))}")
    logging.info(f"Processing {len(symbols)} cryptocurrencies")
    
    # Initialize results dictionary
    historical_data = {}
    new_coins = []
    cached_coins = []
    missing_coins = []
    
    # First, try to get all data from cache
    for symbol in symbols:
        cache_key = f'crypto_historical_{symbol}'
        cached_data = cache.get(cache_key)
        
        if cached_data is not None and cached_data.get('data', {}).get('price', []):
            # Convert cached data to DataFrame
            data = pd.DataFrame(
                cached_data['data'],
                index=pd.to_datetime(cached_data['index'])
            )
            historical_data[symbol] = data
            cached_coins.append(symbol)
        else:
            missing_coins.append(symbol)
    
    logging.info(f"Found {len(cached_coins)} coins in cache")
    if missing_coins:
        logging.info(f"Fetching data for {len(missing_coins)} missing coins")
        
        # Now fetch only the missing coins
        for symbol in missing_coins:
            try:
                data = get_historical_crypto_data(symbol)
                if not data.empty:
                    historical_data[symbol] = data
                    new_coins.append(symbol)
                time.sleep(0.1)  # Add small delay to avoid rate limits
            except Exception as e:
                logging.error(f"Error processing {symbol}: {str(e)}")
    
    # Log summary
    logging.info(f"Successfully loaded {len(historical_data)} coins total")
    logging.info(f"- {len(cached_coins)} from cache: {', '.join(cached_coins[:5])}{'...' if len(cached_coins) > 5 else ''}")
    logging.info(f"- {len(new_coins)} newly fetched: {', '.join(new_coins)}")
    
    missing_count = len(symbols) - len(historical_data)
    if missing_count > 0:
        logging.warning(f"Unable to fetch data for {missing_count} coins")
    
    return historical_data 