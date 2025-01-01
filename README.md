# Crypto Market Sentiment Analyzer

A real-time cryptocurrency market sentiment analysis tool that tracks correlations between different cryptocurrencies, market indicators, and the Fear & Greed Index.

## Features

- Real-time tracking of top 50 cryptocurrencies
- Correlation analysis between cryptocurrencies
- Market sentiment analysis using Fear & Greed Index
- Comparison with traditional market indicators (S&P 500, VIX)
- Interactive visualizations using Streamlit
- Efficient data caching system

## Setup

1. Clone the repository:

```bash
git clone https://github.com/Ethanderson03/CryptoSentimentAnalysis.git
cd CryptoSentimentAnalysis
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up your environment variables:

- Copy `.env.template` to `.env`
- Add your CoinMarketCap API key to the `.env` file

4. Run the application:

```bash
streamlit run app.py
```

## Data Sources

- Cryptocurrency data: CoinMarketCap API (with yfinance fallback)
- S&P 500 and VIX data: yfinance
- Fear & Greed Index: Alternative.me API

## Features

- Real-time market data visualization
- Correlation analysis between different assets
- Rolling correlation analysis
- Interactive data selection and filtering
- Automatic data caching for improved performance
