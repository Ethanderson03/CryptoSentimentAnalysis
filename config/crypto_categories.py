"""
Configuration file defining cryptocurrency categories/baskets
"""

CRYPTO_CATEGORIES = {
    'Layer1': [
        'BTC',  # Bitcoin
        'ETH',  # Ethereum
        'SOL',  # Solana
        'ADA',  # Cardano
        'AVAX', # Avalanche
        'NEAR', # NEAR Protocol
        'FTM',  # Fantom
        'ALGO', # Algorand
        'ETC',  # Ethereum Classic
        'ICP',  # Internet Computer
        'HBAR', # Hedera
        'EOS',  # EOS
    ],
    'Layer2': [
        'OP',   # Optimism
        'ARB',  # Arbitrum
        'STX',  # Stacks
        'IMX',  # Immutable X
        'MNT',  # Mantle
    ],
    'DeFi': [
        'UNI',  # Uniswap
        'AAVE', # Aave
        'MKR',  # Maker
        'LDO',  # Lido DAO
        'CRV',  # Curve
        'INJ',  # Injective
        'RUNE', # THORChain
        'DYDX', # dYdX
    ],
    'Exchange': [
        'BNB',  # Binance
        'OKB',  # OKX
        'CRO',  # Crypto.com
        'KCS',  # KuCoin
        'GT',   # Gate
        'LEO',  # UNUS SED LEO
    ],
    'Infrastructure': [
        'LINK', # Chainlink
        'GRT',  # The Graph
        'QNT',  # Quant
        'THETA',# Theta Network
        'FIL',  # Filecoin
        'AR',   # Arweave
        'FET',  # Fetch.ai
    ],
    'Cross-Chain': [
        'ATOM', # Cosmos
        'DOT',  # Polkadot
        'XRP',  # Ripple
        'TRX',  # TRON
        'XLM',  # Stellar
        'IOTA', # IOTA
    ],
    'Gaming': [
        'SAND', # The Sandbox
        'GALA', # Gala
        'IMX',  # Immutable X
        'ENS',  # Ethereum Name Service
        'FLOW', # Flow
    ],
    'Meme': [
        'DOGE', # Dogecoin
        'SHIB', # Shiba Inu
        'PEPE', # Pepe
        'FLOKI',# Floki
        'WIF',  # Worldcoin
    ],
    'Stablecoins': [
        'USDT', # Tether
        'USDC', # USD Coin
        'FDUSD',# First Digital USD
        'DAI',  # Dai
        'USDe', # USD Edge
    ],
    'Privacy': [
        'XMR',  # Monero
        'BCH',  # Bitcoin Cash
        'XTZ',  # Tezos
        'BSV',  # Bitcoin SV
    ]
} 