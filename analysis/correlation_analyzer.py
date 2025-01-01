import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import logging

def calculate_crypto_correlations(crypto_data):
    """Calculate correlations between different cryptocurrencies.
    
    Args:
        crypto_data: Dict mapping coin symbols to DataFrames with historical price and market cap
    Returns:
        DataFrame with correlation matrix
    """
    # Create a DataFrame with all crypto prices
    prices_df = pd.DataFrame()
    for symbol, data in crypto_data.items():
        prices_df[symbol] = data['price']
    
    # Calculate correlation matrix
    return prices_df.corr()

def create_correlation_heatmap(correlation_matrix):
    """Create a heatmap visualization of correlations.
    
    Args:
        correlation_matrix: DataFrame with correlation values
    Returns:
        Plotly figure object
    """
    fig = go.Figure(data=go.Heatmap(
        z=correlation_matrix,
        x=correlation_matrix.columns,
        y=correlation_matrix.columns,
        colorscale='RdBu',
        zmin=-1,
        zmax=1,
        text=np.round(correlation_matrix, 2),  # Show correlation values
        texttemplate='%{text}',
        textfont={"size": 10},
        hoverongaps=False,
    ))
    
    fig.update_layout(
        title='Market Correlations',
        height=800,  # Increased height for better readability
        width=1000,  # Increased width for better readability
        xaxis={'side': 'bottom'},  # Show x-axis labels at bottom
        yaxis={'autorange': 'reversed'},  # Reverse y-axis to match traditional correlation matrix display
    )
    
    return fig

def calculate_market_correlations(crypto_data, sp500_data, vix_data, fear_greed_data):
    """Calculate correlations between crypto and traditional market indicators.
    
    Args:
        crypto_data: Dict mapping coin symbols to DataFrames with historical price and market cap
        sp500_data: Series with S&P 500 historical data
        vix_data: Series with VIX historical data
        fear_greed_data: Series with Fear & Greed Index data
    Returns:
        DataFrame with correlation matrix
    """
    # Print input data info
    print("\nInput data shapes:")
    print(f"S&P 500: {len(sp500_data) if sp500_data is not None else 'None'}")
    print(f"VIX: {len(vix_data) if vix_data is not None else 'None'}")
    print(f"Fear & Greed: {len(fear_greed_data) if fear_greed_data is not None else 'None'}")
    
    # Create a DataFrame with crypto prices first
    market_df = pd.DataFrame()
    
    # Filter out coins with too much missing data
    valid_coins = {}
    for symbol, data in crypto_data.items():
        daily_price = data['price'].resample('D').last()
        if len(daily_price.dropna()) > 200:  # Only keep coins with sufficient data
            valid_coins[symbol] = daily_price
    
    logging.info(f"Found {len(valid_coins)} coins with sufficient data")
    
    # Add valid coins to the dataframe
    for symbol, price_series in valid_coins.items():
        market_df[symbol] = price_series
    
    # Add market indicators
    if sp500_data is not None:
        market_df['SP500'] = sp500_data.resample('D').last()
    if vix_data is not None:
        market_df['VIX'] = vix_data.resample('D').last()
    if fear_greed_data is not None:
        if not isinstance(fear_greed_data.index, pd.DatetimeIndex):
            fear_greed_data.index = pd.to_datetime(fear_greed_data.index)
        market_df['Fear_Greed'] = fear_greed_data
    
    # Ensure all indices are timezone-naive
    market_df.index = pd.to_datetime(market_df.index)
    if market_df.index.tz is not None:
        market_df.index = market_df.index.tz_convert('UTC').tz_localize(None)
    
    # Align dates to only include days where we have all data
    start_date = max(market_df[col].first_valid_index() for col in market_df.columns)
    end_date = min(market_df[col].last_valid_index() for col in market_df.columns)
    market_df = market_df.loc[start_date:end_date]
    
    # Print debug information
    print("\nData shape before alignment:", market_df.shape)
    print("Column names:", market_df.columns.tolist())
    print("Date range:", market_df.index.min(), "to", market_df.index.max())
    print("\nSample of data:")
    print(market_df.head())
    print("\nNaN counts before dropping:")
    print(market_df.isna().sum())
    
    # Drop any rows with NaN values
    market_df = market_df.dropna()
    print("\nData shape after dropping NaN:", market_df.shape)
    
    # Calculate correlations
    return market_df.corr()

def calculate_rolling_correlations(crypto_data, sp500_data, window=30):
    """Calculate rolling correlations between crypto and S&P 500.
    
    Args:
        crypto_data: Dict mapping coin symbols to DataFrames with historical price and market cap
        sp500_data: Series with S&P 500 historical data
        window: Rolling window size in days
    Returns:
        DataFrame with rolling correlations
    """
    # Create a DataFrame with crypto prices first
    rolling_corr_df = pd.DataFrame()
    
    # Filter out coins with too much missing data
    valid_coins = {}
    for symbol, data in crypto_data.items():
        daily_price = data['price'].resample('D').last()
        if len(daily_price.dropna()) > 200:  # Only keep coins with sufficient data
            valid_coins[symbol] = daily_price
    
    logging.info(f"Found {len(valid_coins)} coins with sufficient data for rolling correlations")
    
    for symbol, crypto_daily in valid_coins.items():
        # Resample S&P 500 data to daily frequency
        sp500_daily = sp500_data.resample('D').last()
        
        # Align dates between crypto and S&P 500
        aligned_data = pd.DataFrame({
            'crypto': crypto_daily,
            'sp500': sp500_daily
        })
        
        # Drop any NaN values
        aligned_data = aligned_data.dropna()
        
        if not aligned_data.empty:
            # Calculate rolling correlation with smaller min_periods
            rolling_corr = aligned_data['crypto'].rolling(
                window=window,
                min_periods=max(5, window//4)  # Use at least 5 periods or 1/4 of window
            ).corr(aligned_data['sp500'])
            
            rolling_corr_df[symbol] = rolling_corr
    
    # Print debug information
    print(f"\nRolling correlation shape: {rolling_corr_df.shape}")
    if not rolling_corr_df.empty:
        print(f"Date range: {rolling_corr_df.index.min()} to {rolling_corr_df.index.max()}")
        print(f"Sample of rolling correlations:")
        print(rolling_corr_df.head())
    print(f"NaN counts:")
    print(rolling_corr_df.isna().sum())
    
    return rolling_corr_df.dropna()

def plot_rolling_correlations(rolling_corr_df):
    """Create a line plot of rolling correlations.
    
    Args:
        rolling_corr_df: DataFrame with rolling correlations
    Returns:
        Plotly figure object
    """
    fig = go.Figure()
    
    for column in rolling_corr_df.columns:
        fig.add_trace(
            go.Scatter(
                x=rolling_corr_df.index,
                y=rolling_corr_df[column],
                name=f'{column} vs S&P 500',
                mode='lines'
            )
        )
    
    fig.update_layout(
        title=f'{rolling_corr_df.shape[0]}-Day Rolling Correlations with S&P 500',
        yaxis_title='Correlation Coefficient',
        yaxis=dict(range=[-1, 1]),  # Fix y-axis range to standard correlation range
        height=600,
        width=1000,
        showlegend=True,
        hovermode='x unified'  # Show all values for a given x-coordinate
    )
    
    # Add horizontal reference lines
    fig.add_hline(y=0, line=dict(color="gray", width=1, dash="dash"))
    fig.add_hline(y=0.5, line=dict(color="gray", width=1, dash="dot"))
    fig.add_hline(y=-0.5, line=dict(color="gray", width=1, dash="dot"))
    
    return fig 