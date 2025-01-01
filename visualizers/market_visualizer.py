import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

def create_visualization(sp500_data=None, vix_data=None, fear_greed_data=None, crypto_historical_data=None, selected_metric="Price"):
    """Create an interactive visualization using plotly
    
    Args:
        sp500_data: Series with S&P 500 historical data
        vix_data: Series with VIX historical data
        fear_greed_data: Series with Fear & Greed Index data
        crypto_historical_data: Dict mapping coin symbols to DataFrames with historical price and market cap
        selected_metric: Either "Price" or "Market Cap"
    """
    # Create figure with four subplots
    fig = make_subplots(rows=4, cols=1, 
                       subplot_titles=('S&P 500', 'VIX', 'Cryptocurrency Markets', 'Crypto Fear & Greed Index'),
                       row_heights=[0.25, 0.25, 0.25, 0.25],
                       vertical_spacing=0.1)

    # Add S&P 500 data
    if sp500_data is not None:
        fig.add_trace(
            go.Scatter(x=sp500_data.index, y=sp500_data.round(2), 
                      name='S&P 500',
                      line=dict(color='black', width=2)),
            row=1, col=1
        )
    
    # Add VIX data
    if vix_data is not None:
        fig.add_trace(
            go.Scatter(x=vix_data.index, y=vix_data.round(2),
                      name='VIX',
                      line=dict(color='red', width=2)),
            row=2, col=1
        )

    # Add cryptocurrency data
    if crypto_historical_data:
        colors = ['blue', 'red', 'green', 'orange', 'purple']
        
        # Add traces for each cryptocurrency
        for i, (symbol, data) in enumerate(crypto_historical_data.items()):
            color = colors[i % len(colors)]
            metric_key = 'market_cap' if selected_metric == "Market Cap" else 'price'
            
            fig.add_trace(
                go.Scatter(x=data.index, y=data[metric_key].round(2),
                          name=f'{symbol} {selected_metric}',
                          line=dict(color=color)),
                row=3, col=1
            )

    # Add Fear & Greed Index
    if fear_greed_data is not None:
        fig.add_trace(
            go.Scatter(x=fear_greed_data.index, y=fear_greed_data.round(0),
                      name='Fear & Greed Index',
                      line=dict(color='purple', width=2)),
            row=4, col=1
        )
        
        # Add reference lines for Fear & Greed
        fig.add_hline(y=25, line=dict(color="red", width=1, dash="dash"), row=4, col=1)
        fig.add_hline(y=75, line=dict(color="green", width=1, dash="dash"), row=4, col=1)

    # Update layout
    fig.update_layout(
        height=1200,  # Increased height for four subplots
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="right",
            x=0.99
        ),
        margin=dict(t=30, b=30)
    )

    # Update y-axes labels and format
    fig.update_yaxes(title_text="Value (USD)", row=1, col=1, tickformat=".2f")
    fig.update_yaxes(title_text="VIX Index", row=2, col=1, tickformat=".2f")
    fig.update_yaxes(title_text=f"{selected_metric} (USD)", type="log", row=3, col=1, tickformat=".2f")
    fig.update_yaxes(title_text="Index Value", range=[0, 100], row=4, col=1, tickformat="d")
    
    # Update x-axes
    fig.update_xaxes(rangeslider_visible=False)
    fig.update_xaxes(title_text="Date", row=4, col=1)
    
    # Format all x-axes to show clean dates
    for i in range(1, 5):
        fig.update_xaxes(row=i, col=1, tickformat="%Y-%m-%d")

    return fig 