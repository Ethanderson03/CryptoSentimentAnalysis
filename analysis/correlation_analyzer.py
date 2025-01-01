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
    return df.pct_change().fillna(0)

def calculate_category_correlations(df, window_size=30):
    """Calculate correlations between different categories of cryptocurrencies"""
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
    
    # Combine all category series into a single dataframe
    category_df = pd.DataFrame(category_dfs)
    
    # Calculate correlations
    correlations = category_df.corr()
    return correlations

def calculate_crypto_correlations(crypto_data):
    """Calculate correlations between cryptocurrencies and categories"""
    if not crypto_data:
        return None
    
    # Convert individual coins to dataframe
    df = pd.DataFrame({symbol: data['price'] for symbol, data in crypto_data.items()})
    
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

def create_correlation_heatmap(correlation_matrix):
    """Create a heatmap visualization of correlations"""
    if correlation_matrix is None:
        return None
        
    fig = px.imshow(
        correlation_matrix,
        color_continuous_scale='RdBu',
        aspect='auto',
        title='Correlation Heatmap',
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

def calculate_market_correlations(crypto_data, sp500_data, vix_data, fear_greed_data):
    """Calculate correlations between crypto and market indicators"""
    if not crypto_data or sp500_data is None:
        return None
    
    # Prepare market data
    market_data = pd.DataFrame()
    
    # Add market indicators
    if sp500_data is not None:
        market_data['SP500'] = sp500_data
    if vix_data is not None:
        market_data['VIX'] = vix_data
    if fear_greed_data is not None:
        market_data['Fear_Greed'] = fear_greed_data
    
    # Add individual crypto data
    for symbol, data in crypto_data.items():
        market_data[f"{symbol}"] = data['price']
    
    # Add category indices
    for category in CRYPTO_CATEGORIES.keys():
        coins = CRYPTO_CATEGORIES[category]
        available_coins = [coin for coin in coins if coin in crypto_data]
        if available_coins:
            category_prices = [crypto_data[coin]['price'] for coin in available_coins]
            market_data[f'{category}_Index'] = pd.concat(category_prices, axis=1).mean(axis=1)
    
    # Calculate returns for price data (except Fear & Greed which is already a sentiment score)
    returns_cols = [col for col in market_data.columns if col != 'Fear_Greed']
    market_returns = market_data.copy()
    market_returns[returns_cols] = calculate_returns(market_data[returns_cols])
    
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
    
    # Create a dataframe with crypto and S&P 500 data
    df = pd.DataFrame()
    
    # Add individual coins
    for symbol, data in crypto_data.items():
        df[symbol] = data['price']
    
    # Add category indices
    for category in CRYPTO_CATEGORIES.keys():
        coins = CRYPTO_CATEGORIES[category]
        available_coins = [coin for coin in coins if coin in crypto_data]
        if available_coins:
            category_prices = [crypto_data[coin]['price'] for coin in available_coins]
            df[f'{category}_Index'] = pd.concat(category_prices, axis=1).mean(axis=1)
    
    # Add S&P 500
    df['SP500'] = sp500_data
    
    # Calculate returns
    returns_df = calculate_returns(df)
    
    # Calculate rolling correlations with S&P 500
    rolling_corr = returns_df.rolling(window=window, min_periods=window//2).corr()
    
    # Extract only the correlations with S&P 500
    sp500_corr = rolling_corr.xs('SP500', level=1)
    sp500_corr = sp500_corr.drop('SP500', axis=1)
    
    logging.info(f"Found {len(df.columns)-1} assets with sufficient data for rolling correlations")
    
    return sp500_corr

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
        title='30-Day Rolling Correlation with S&P 500'
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