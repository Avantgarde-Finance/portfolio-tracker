import json
from pathlib import Path

ABI_DIR = Path(__file__).parent / "abi"


def load_abi(filename: str) -> list:
    with open(ABI_DIR / filename) as f:
        return json.load(f)


AAVE_POOL_ABI = load_abi("aave_pool.json")
AAVE_POOL_DATA_PROVIDER_ABI = load_abi("aave_pool_data_provider.json")
ERC20_ABI = load_abi("erc20.json")

AAVE_V3_CONTRACTS = {
    'ethereum': {
        'pool': '0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2',
        'pool_data_provider': '0x7B4EB56E7CD4b454BA8ff71E4518426369a138a3',
        'oracle': '0x54586bE62E3c3580375aE3723C145253060Ca0C2'
    },
    'arbitrum': {
        'pool': '0x794a61358D6845594F94dc1DB02A252b5b4814aD',
        'pool_data_provider': '0x69FA688f1Dc47d4B5d8029D5a35FB7a548310654',
        'oracle': '0xb56c2F0B653B2e0b10C9b928C8580Ac5Df02C7C7'
    }
}

CHAIN_ID_TO_NAME = {1: 'Ethereum', 42161: 'Arbitrum', 8453: 'Base', 10: 'Optimism'}
CHAIN_NAME_TO_ID = {v: k for k, v in CHAIN_ID_TO_NAME.items()}

DEFAULT_RPC_URLS = {
    'Ethereum': 'https://ethereum-rpc.publicnode.com',
    'Arbitrum': 'https://arbitrum-one-rpc.publicnode.com',
    'Base': 'https://base-rpc.publicnode.com',
    'Optimism': 'https://optimism-rpc.publicnode.com',
}

# Hardcoded fallback token lists (used when DB is unavailable)
FALLBACK_TOKEN_DATA = {
    'Ethereum': {
        'USDC': {'address': '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48', 'decimals': 6, 'coingecko_id': 'usd-coin', 'price_source': 1},
        'USDT': {'address': '0xdAC17F958D2ee523a2206206994597C13D831ec7', 'decimals': 6, 'coingecko_id': 'tether', 'price_source': 1},
        'DAI': {'address': '0x6B175474E89094C44Da98b954EedeAC495271d0F', 'decimals': 18, 'coingecko_id': 'dai', 'price_source': 1},
        'WBTC': {'address': '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599', 'decimals': 8, 'coingecko_id': 'wrapped-bitcoin', 'price_source': 1},
        'WETH': {'address': '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2', 'decimals': 18, 'coingecko_id': 'weth', 'price_source': 1},
        'LINK': {'address': '0x514910771AF9Ca656af840dff83E8264EcF986CA', 'decimals': 18, 'coingecko_id': 'chainlink', 'price_source': 1},
        'UNI': {'address': '0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984', 'decimals': 18, 'coingecko_id': 'uniswap', 'price_source': 1},
        'AAVE': {'address': '0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9', 'decimals': 18, 'coingecko_id': 'aave', 'price_source': 1},
        'stETH': {'address': '0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84', 'decimals': 18, 'coingecko_id': 'lido-staked-ether', 'price_source': 1},
        'wstETH': {'address': '0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0', 'decimals': 18, 'coingecko_id': 'wrapped-steth', 'price_source': 1},
    },
    'Arbitrum': {
        'USDC': {'address': '0xaf88d065e77c8cC2239327C5EDb3A432268e5831', 'decimals': 6, 'coingecko_id': 'usd-coin', 'price_source': 1},
        'USDT': {'address': '0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9', 'decimals': 6, 'coingecko_id': 'tether', 'price_source': 1},
        'DAI': {'address': '0xDA10009cBd5D07dd0CeCc66161FC93D7c9000da1', 'decimals': 18, 'coingecko_id': 'dai', 'price_source': 1},
        'WBTC': {'address': '0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f', 'decimals': 8, 'coingecko_id': 'wrapped-bitcoin', 'price_source': 1},
        'WETH': {'address': '0x82aF49447D8a07e3bd95BD0d56f35241523fBab1', 'decimals': 18, 'coingecko_id': 'weth', 'price_source': 1},
        'ARB': {'address': '0x912CE59144191C1204E64559FE8253a0e49E6548', 'decimals': 18, 'coingecko_id': 'arbitrum', 'price_source': 1},
        'LINK': {'address': '0xf97f4df75117a78c1A5a0DBb814Af92458539FB4', 'decimals': 18, 'coingecko_id': 'chainlink', 'price_source': 1},
        'USND': {'address': '0x4ecf61a6c2FaB8A047CEB3B3B263B401763e9D49', 'decimals': 18, 'coingecko_id': 'us-nerite-dollar', 'price_source': 1},
        'tBTC': {'address': '0x6c84a8f1c29108F47a79964b5Fe888D4f4D0dE40', 'decimals': 18, 'coingecko_id': 'tbtc', 'price_source': 1},
    },
}
