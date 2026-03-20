"""CoinGecko API client for current prices."""
import os
import requests
from typing import Dict

import streamlit as st
from dotenv import load_dotenv

load_dotenv()


@st.cache_data(ttl=300)
def fetch_coingecko_prices(coin_ids: str) -> Dict[str, float]:
    """Fetch current prices from CoinGecko /simple/price. Cached 5 min.

    Args:
        coin_ids: Comma-separated CoinGecko IDs (sorted for stable cache key).

    Returns:
        {coingecko_id: usd_price}
    """
    api_key = os.getenv("COINGECKO_API_KEY", "")
    url = "https://pro-api.coingecko.com/api/v3/simple/price"
    params = {"ids": coin_ids, "vs_currencies": "usd"}
    headers = {"accept": "application/json", "x-cg-pro-api-key": api_key}

    response = requests.get(url, params=params, headers=headers, timeout=10)
    response.raise_for_status()
    data = response.json()

    return {cg_id: info["usd"] for cg_id, info in data.items() if "usd" in info}
