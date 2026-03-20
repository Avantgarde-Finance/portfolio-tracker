# Multi-Chain Portfolio Tracker

Track wallet positions across Ethereum, Arbitrum, Base, Optimism, Aave V3, and Hyperliquid.

## Features

- **Token balances** — ERC-20 tokens on Ethereum, Arbitrum, Base, and Optimism
- **Native ETH** — ETH balances across all supported chains
- **Aave V3** — Supply/borrow positions with health factor monitoring
- **Hyperliquid** — Open perpetual positions with PnL tracking
- **Multi-source pricing** — CoinGecko, Morpho, Pendle, and Pareto

## Setup

```bash
# Install dependencies
uv sync

# Configure environment
cp .env.example .env
# Edit .env with your DB credentials and CoinGecko API key

# Run
uv run streamlit run main.py
```

## Usage

1. Open the app in your browser
2. Enter a wallet address in the sidebar
3. Click **Scan Portfolio**
4. View balances, positions, and USD values across all chains

## Token not showing up?

The token list is pulled from the database. If a token you hold isn't being tracked, add it here:

**[Token Universe Manager](https://avg-yield-reports.streamlit.app/Token_Universe)**
