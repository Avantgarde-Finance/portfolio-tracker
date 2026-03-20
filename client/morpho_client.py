"""Morpho API client for current vault share prices."""
import time
import requests
from typing import Optional, Dict

import streamlit as st


MORPHO_API_URL = "https://api.morpho.org/graphql"

# V1 query — sharePriceUsd
_V1_QUERY = """
query($address: String!, $chainId: Int!, $options: TimeseriesOptions) {
  vaultByAddress(address: $address, chainId: $chainId) {
    historicalState {
      sharePriceUsd(options: $options) { x y }
    }
  }
}
"""

# V2 query — sharePrice
_V2_QUERY = """
query VaultV2ByAddress($address: String!, $chainId: Int!, $options: TimeseriesOptions) {
  vaultV2ByAddress(address: $address, chainId: $chainId) {
    historicalState {
      sharePrice(options: $options) { x y }
    }
  }
}
"""


def _query_morpho(query: str, vault_key: str, price_key: str,
                  address: str, chain_id: int) -> Optional[float]:
    """Execute a Morpho GraphQL query and return the latest price."""
    now = int(time.time())
    options = {"interval": "DAY", "startTimestamp": now - 86400, "endTimestamp": now}
    variables = {"address": address, "chainId": chain_id, "options": options}

    resp = requests.post(
        MORPHO_API_URL,
        json={"query": query, "variables": variables},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()

    if "errors" in data:
        raise Exception(data["errors"][0].get("message", "Unknown error"))

    vault = data.get("data", {}).get(vault_key)
    if not vault:
        return None

    entries = vault.get("historicalState", {}).get(price_key, [])
    if not entries:
        return None

    # Return the most recent entry
    return float(entries[-1]["y"])


@st.cache_data(ttl=300)
def fetch_morpho_v1_price(address: str, chain_id: int) -> Optional[float]:
    """Get current share price USD for a Morpho V1 vault. Cached 5 min."""
    return _query_morpho(_V1_QUERY, "vaultByAddress", "sharePriceUsd",
                         address, chain_id)


@st.cache_data(ttl=300)
def fetch_morpho_v2_price(address: str, chain_id: int) -> Optional[float]:
    """Get current share price for a Morpho V2 vault. Cached 5 min."""
    return _query_morpho(_V2_QUERY, "vaultV2ByAddress", "sharePrice",
                         address, chain_id)
