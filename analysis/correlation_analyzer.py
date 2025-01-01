"""
Functions for analyzing correlations between different market indicators
"""
import pandas as pd
import numpy as np
import plotly.express as px
from config.crypto_categories import CRYPTO_CATEGORIES
import logging

def get_coin_category(symbol):
    """Return the category of a given coin symbol"""
    for category, coins in CRYPTO_CATEGORIES.items():
        if symbol in coins:
            return category
    return 'Other'

def calculate_returns(df):
    """Calculate percentage returns from price data"""
    if df.empty:
        return pd.DataFrame()
    return df.pct_change().fillna(0)

def align_market_data(crypto_data, traditional_data):
    """
    Align crypto and traditional market data considering different trading schedules.
    Traditional markets only trade Monday-Friday during market hours.
    """
    if crypto_data.empty or traditional_data.empty:
        return pd.DataFrame()
        
    # Resample both to daily frequency first (use last price of the day)
    crypto_daily = crypto_data.resample('D').last()
    trad_daily = traditional_data.resample('D').last()
    
    # Forward fill traditional market data for weekends
    trad_daily = trad_daily.ffill()
    
    # Align both datasets
    aligned_data = pd.concat([crypto_daily, trad_daily], axis=1)
    
    # Only keep rows where we have both crypto and traditional market data
    aligned_data = aligned_data.dropna(how='any')
    
    # Only keep business days (Monday-Friday)
    aligned_data = aligned_data[aligned_data.index.dayofweek < 5]
    
    return aligned_data

def calculate_category_correlations(df, window_size=30):
    """Calculate correlations between different categories of cryptocurrencies"""
    if df.empty:
        return pd.DataFrame()
        
    # Create category dataframes
    category_dfs = {}
    for category in CRYPTO_CATEGORIES.keys():
        coins = CRYPTO_CATEGORIES[category]
        # Filter coins that exist in our dataframe
        available_coins = [coin for coin in coins if coin in df.columns]
        if available_coins:
            # Calculate the average return for the category
            category_returns = calculate_returns(df[available_coins])
            category_dfs[category] = category_returns.mean(axis=1)
    
    if not category_dfs:
        return pd.DataFrame()
        
    # Combine all category series into a single dataframe
    category_df = pd.DataFrame(category_dfs)
    
    # Calculate correlations
    correlations = category_df.corr()
    return correlations

def calculate_crypto_correlations(crypto_data):
    """Calculate correlations between cryptocurrencies and categories"""
    if not crypto_data:
        return pd.DataFrame()
    
    # Convert individual coins to dataframe
    df = pd.DataFrame({symbol: data['price'] for symbol, data in crypto_data.items()})
    
    if df.empty:
        return pd.DataFrame()
    
    # Calculate returns for individual coins
    returns_df = calculate_returns(df)
    
    # Add category indices
    for category in CRYPTO_CATEGORIES.keys():
        coins = CRYPTO_CATEGORIES[category]
        available_coins = [coin for coin in coins if coin in df.columns]
        if available_coins:
            # Calculate the average return for the category
            category_returns = calculate_returns(df[available_coins])
            returns_df[f"{category}_Index"] = category_returns.mean(axis=1)
    
    if returns_df.empty:
        return pd.DataFrame()
    
    # Calculate correlations
    correlations = returns_df.corr()
    
    # Add category information to individual coins
    new_index = []
    new_columns = []
    for idx in correlations.index:
        if idx.endswith('_Index'):
            new_index.append(idx)
            new_columns.append(idx)
        else:
            new_index.append(f"{idx} ({get_coin_category(idx)})")
            new_columns.append(f"{idx} ({get_coin_category(idx)})")
    
    correlations.index = new_index
    correlations.columns = new_columns
    
    return correlations

def calculate_market_correlations(crypto_data, sp500_data, vix_data, fear_greed_data):
    """Calculate correlations between crypto and market indicators"""
    if not crypto_data or sp500_data is None:
        return pd.DataFrame()
    
    # Prepare market data
    market_data = pd.DataFrame()
    
    # Add market indicators with proper time alignment
    if sp500_data is not None:
        market_data['SP500'] = sp500_data
    if vix_data is not None:
        market_data['VIX'] = vix_data
    if fear_greed_data is not None:
        market_data['Fear_Greed'] = fear_greed_data
    
    if market_data.empty:
        return pd.DataFrame()
    
    # Add individual crypto data
    crypto_df = pd.DataFrame()
    for symbol, data in crypto_data.items():
        crypto_df[symbol] = data['price']
    
    if crypto_df.empty:
        return pd.DataFrame()
    
    # Add category indices
    for category in CRYPTO_CATEGORIES.keys():
        coins = CRYPTO_CATEGORIES[category]
        available_coins = [coin for coin in coins if coin in crypto_data]
        if available_coins:
            category_prices = [crypto_data[coin]['price'] for coin in available_coins]
            crypto_df[f'{category}_Index'] = pd.concat(category_prices, axis=1).mean(axis=1)
    
    # Align crypto and traditional market data
    aligned_data = align_market_data(crypto_df, market_data)
    
    if aligned_data.empty:
        return pd.DataFrame()
    
    # Calculate returns for price data (except Fear & Greed which is already a sentiment score)
    returns_cols = [col for col in aligned_data.columns if col != 'Fear_Greed']
    market_returns = aligned_data.copy()
    
    # Calculate returns and handle missing values
    market_returns[returns_cols] = calculate_returns(aligned_data[returns_cols])
    market_returns = market_returns.ffill()  # Forward fill missing values
    
    # Drop any remaining NaN values
    market_returns = market_returns.dropna()
    
    if market_returns.empty:
        return pd.DataFrame()
    
    # Calculate correlations
    correlations = market_returns.corr()
    
    # Log statistics about coins by category
    for category in CRYPTO_CATEGORIES:
        coins = CRYPTO_CATEGORIES[category]
        available = [c for c in coins if c in crypto_data]
        logging.info(f"{category}: {len(available)}/{len(coins)} coins available")
    
    return correlations

def calculate_rolling_correlations(crypto_data, sp500_data, window=30):
    """Calculate rolling correlations between crypto and S&P 500"""
    if not crypto_data or sp500_data is None:
        return pd.DataFrame()
    
    # Create a dataframe with crypto data
    crypto_df = pd.DataFrame()
    
    # Add individual coins
    for symbol, data in crypto_data.items():
        crypto_df[symbol] = data['price']
    
    if crypto_df.empty:
        return pd.DataFrame()
    
    # Add category indices
    for category in CRYPTO_CATEGORIES.keys():
        coins = CRYPTO_CATEGORIES[category]
        available_coins = [coin for coin in coins if coin in crypto_data]
        if available_coins:
            category_prices = [crypto_data[coin]['price'] for coin in available_coins]
            crypto_df[f'{category}_Index'] = pd.concat(category_prices, axis=1).mean(axis=1)
    
    # Create traditional market dataframe
    trad_df = pd.DataFrame({'SP500': sp500_data})
    
    # Align crypto and traditional market data
    aligned_data = align_market_data(crypto_df, trad_df)
    
    if aligned_data.empty:
        return pd.DataFrame()
    
    # Calculate returns and handle missing values
    returns_df = calculate_returns(aligned_data)
    returns_df = returns_df.ffill()  # Forward fill missing values
    returns_df = returns_df.dropna()  # Drop any remaining NaN values
    
    if returns_df.empty:
        return pd.DataFrame()
    
    # Calculate rolling correlations with S&P 500
    rolling_corr = returns_df.rolling(window=window, min_periods=window//2).corr()
    
    # Extract only the correlations with S&P 500
    sp500_corr = rolling_corr.xs('SP500', level=1)
    sp500_corr = sp500_corr.drop('SP500', axis=1)
    
    logging.info(f"Found {len(aligned_data.columns)-1} assets with sufficient data for rolling correlations")
    
    return sp500_corr

def create_correlation_heatmap(correlation_matrix):
    """Create a heatmap visualization of correlations"""
    if correlation_matrix is None or correlation_matrix.empty:
        return None
        
    fig = px.imshow(
        correlation_matrix,
        color_continuous_scale='RdBu',
        aspect='auto',
        title='Correlation Heatmap (Business Days Only)',
        zmin=-1,
        zmax=1
    )
    
    # Update layout for better readability
    fig.update_layout(
        height=1000,  # Increased height for more coins
        width=1000,   # Increased width for more coins
        title_x=0.5,
        title_y=0.95
    )
    
    # Rotate x-axis labels for better readability
    fig.update_xaxes(tickangle=45)
    
    return fig

def plot_rolling_correlations(rolling_corr):
    """Create a line plot of rolling correlations"""
    if rolling_corr.empty:
        return None
    
    # Separate individual coins and indices
    indices = [col for col in rolling_corr.columns if col.endswith('_Index')]
    coins = [col for col in rolling_corr.columns if not col.endswith('_Index')]
    
    # Create figure with two traces
    fig = px.line(
        rolling_corr,
        title='30-Day Rolling Correlation with S&P 500 (Business Days Only)'
    )
    
    # Update colors to distinguish between coins and indices
    for trace in fig.data:
        if trace.name in indices:
            trace.line.width = 3  # Make index lines thicker
            trace.line.dash = 'solid'
        else:
            trace.line.width = 1  # Make coin lines thinner
            trace.line.dash = 'dot'
    
    # Update layout
    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Correlation Coefficient',
        height=800,  # Increased height for more lines
        showlegend=True,
        title_x=0.5,
        title_y=0.95,
        legend=dict(
            yanchor="top",
            y=-0.2,
            xanchor="center",
            x=0.5,
            orientation="h"
        ),
        yaxis=dict(
            range=[-1, 1],  # Fix y-axis range to correlation bounds
            gridcolor='lightgray',
            zerolinecolor='gray',
            zerolinewidth=2
        )
    )
    
    # Add reference lines
    fig.add_hline(y=0.5, line_dash="dot", line_color="gray", opacity=0.5)
    fig.add_hline(y=-0.5, line_dash="dot", line_color="gray", opacity=0.5)
    
    return fig