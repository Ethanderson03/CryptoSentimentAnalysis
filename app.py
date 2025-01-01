"""
Main Streamlit application file
"""
import streamlit as st
import logging
from datetime import datetime, timedelta
from data_fetchers.sp500_fetcher import get_sp500_data
from data_fetchers.vix_fetcher import get_vix_data
from data_fetchers.fear_greed_fetcher import get_crypto_fear_greed
from data_fetchers.crypto_fetcher import get_all_historical_data
from visualizers.market_visualizer import create_visualization
from analysis.correlation_analyzer import (
    calculate_crypto_correlations,
    create_correlation_heatmap,
    calculate_market_correlations,
    calculate_rolling_correlations,
    plot_rolling_correlations,
    calculate_category_correlations,
    get_coin_category
)
from config.crypto_categories import CRYPTO_CATEGORIES
import pandas as pd
import plotly.express as px

# Configure logging with more detail
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def initialize_session_state():
    """Initialize session state variables if they don't exist"""
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False
    if 'last_update' not in st.session_state:
        st.session_state.last_update = None
    if 'sp500_data' not in st.session_state:
        st.session_state.sp500_data = None
    if 'vix_data' not in st.session_state:
        st.session_state.vix_data = None
    if 'fear_greed_data' not in st.session_state:
        st.session_state.fear_greed_data = None
    if 'crypto_historical_data' not in st.session_state:
        st.session_state.crypto_historical_data = {}

def should_refresh_data(force_refresh=False):
    """Check if data should be refreshed based on last update time"""
    if force_refresh or not st.session_state.data_loaded:
        return True
    
    if st.session_state.last_update is None:
        return True
    
    # Refresh if last update was more than 12 hours ago
    refresh_threshold = timedelta(hours=12)
    time_since_update = datetime.now() - st.session_state.last_update
    return time_since_update > refresh_threshold

def load_all_data(force_refresh=False):
    """Load all required data and return it"""
    initialize_session_state()
    
    # Check if we need to refresh the data
    if not should_refresh_data(force_refresh):
        logging.info("Using cached data from previous load")
        return (
            st.session_state.sp500_data,
            st.session_state.vix_data,
            st.session_state.fear_greed_data,
            st.session_state.crypto_historical_data,
            {"success": True, "messages": []}
        )
    
    data_status = {"success": True, "messages": []}
    logging.info("Loading market data...")
    
    # Load market data
    sp500_data = get_sp500_data()
    if sp500_data is None:
        data_status["success"] = False
        data_status["messages"].append("Failed to fetch S&P 500 data")
    
    vix_data = get_vix_data()
    if vix_data is None:
        data_status["success"] = False
        data_status["messages"].append("Failed to fetch VIX data")
    
    fear_greed_data = get_crypto_fear_greed()
    if fear_greed_data is None:
        data_status["success"] = False
        data_status["messages"].append("Failed to fetch Fear & Greed data")
    
    # Load cryptocurrency data
    logging.info("Loading cryptocurrency data...")
    try:
        crypto_historical_data = get_all_historical_data()
        if not crypto_historical_data:
            data_status["success"] = False
            data_status["messages"].append("Failed to fetch cryptocurrency data")
        else:
            logging.info(f"Successfully loaded {len(crypto_historical_data)} cryptocurrencies")
    except Exception as e:
        logging.error(f"Error loading cryptocurrency data: {str(e)}")
        data_status["success"] = False
        data_status["messages"].append(f"Failed to fetch cryptocurrency data: {str(e)}")
        crypto_historical_data = {}
    
    # Update session state
    st.session_state.sp500_data = sp500_data
    st.session_state.vix_data = vix_data
    st.session_state.fear_greed_data = fear_greed_data
    st.session_state.crypto_historical_data = crypto_historical_data
    st.session_state.last_update = datetime.now()
    st.session_state.data_loaded = True
    
    return sp500_data, vix_data, fear_greed_data, crypto_historical_data, data_status

def display_correlations(crypto_data, sp500_data, vix_data, fear_greed_data):
    """Display correlation analysis results"""
    # Calculate market correlations
    market_corr = calculate_market_correlations(
        crypto_data, sp500_data, vix_data, fear_greed_data
    )
    
    if not market_corr.empty:
        st.subheader("Market Correlations")
        st.plotly_chart(create_correlation_heatmap(market_corr), use_container_width=True)
    else:
        st.warning("No market correlations available - insufficient data overlap between crypto and traditional markets.")
    
    # Calculate crypto correlations
    crypto_corr = calculate_crypto_correlations(crypto_data)
    
    if not crypto_corr.empty:
        st.subheader("Cryptocurrency Correlations")
        st.plotly_chart(create_correlation_heatmap(crypto_corr), use_container_width=True)
    else:
        st.warning("No cryptocurrency correlations available - insufficient data.")
    
    # Calculate rolling correlations
    rolling_corr = calculate_rolling_correlations(crypto_data, sp500_data)
    
    if not rolling_corr.empty:
        st.subheader("Rolling Correlations with S&P 500")
        st.plotly_chart(plot_rolling_correlations(rolling_corr), use_container_width=True)
    else:
        st.warning("No rolling correlations available - insufficient data overlap between crypto and S&P 500.")

def main():
    # Configure page
    st.set_page_config(layout="wide", menu_items={})
    
    # Remove the default menu and footer
    hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
    """
    st.markdown(hide_menu_style, unsafe_allow_html=True)
    
    st.title("Crypto Market Analysis Dashboard")
    
    # Initialize session state
    initialize_session_state()
    
    # Load data if needed
    sp500_data, vix_data, fear_greed_data, crypto_historical_data, data_status = load_all_data()
    
    # Sidebar controls
    with st.sidebar:
        st.header("Settings")
        
        # Add last update time
        if st.session_state.last_update:
            st.text(f"Last updated: {st.session_state.last_update.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Category selection
        selected_categories = st.multiselect(
            "Select Categories",
            options=list(CRYPTO_CATEGORIES.keys()),
            default=list(CRYPTO_CATEGORIES.keys())[:3]
        )
        
        # Get coins from selected categories
        selected_coins = []
        for category in selected_categories:
            selected_coins.extend(CRYPTO_CATEGORIES[category])
        
        # Additional coin selection
        other_coins = [
            coin for coin in crypto_historical_data.keys()
            if coin not in selected_coins
        ]
        if other_coins:
            additional_coins = st.multiselect(
                "Additional Coins",
                options=other_coins,
                default=[]
            )
            selected_coins.extend(additional_coins)
        
        # Metric selection
        selected_metric = st.radio(
            "Display Metric",
            options=["Price", "Market Cap"]
        )
        
        # Force refresh button
        if st.button("🔄 Force Refresh Data"):
            sp500_data, vix_data, fear_greed_data, crypto_historical_data, data_status = load_all_data(force_refresh=True)
            st.rerun()
    
    # Show any error messages
    if not data_status["success"]:
        st.error("Some data could not be loaded:")
        for msg in data_status["messages"]:
            st.warning(msg)
        st.info("You can try refreshing the data using the button in the sidebar.")
    
    # Filter crypto data based on selection
    filtered_crypto_data = {
        symbol: data for symbol, data in crypto_historical_data.items()
        if symbol in selected_coins
    }
    
    # Create tabs for different views
    tab1, tab2 = st.tabs(["Market Overview", "Correlation Analysis"])
    
    with tab1:
        # Create and display visualization only if we have some data
        if any([sp500_data is not None, 
                vix_data is not None,
                fear_greed_data is not None,
                filtered_crypto_data]):
            fig = create_visualization(
                sp500_data=sp500_data,
                vix_data=vix_data,
                fear_greed_data=fear_greed_data,
                crypto_historical_data=filtered_crypto_data,
                selected_metric=selected_metric
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("No data available to display. Please try refreshing the data.")
    
    with tab2:
        if filtered_crypto_data:
            display_correlations(
                filtered_crypto_data,
                sp500_data,
                vix_data,
                fear_greed_data
            )
        else:
            st.warning("Please select at least one cryptocurrency or category to analyze correlations.")

if __name__ == "__main__":
    main() 