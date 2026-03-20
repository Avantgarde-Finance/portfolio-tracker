"""Pendle API client for current token prices."""
import csv
from io import StringIO
from typing import Optional

import requests
import streamlit as st


@st.cache_data(ttl=300)
def fetch_pendle_price(token_address: str, chain_id: int) -> Optional[float]:
    """Get latest close price for a Pendle token. Cached 5 min."""
    url = f"https://api-v2.pendle.finance/core/v4/{chain_id}/prices/{token_address}/ohlcv"
    params = {"time_frame": "day"}

    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    csv_data = data.get("results", "")
    if not csv_data:
        return None

    rows = list(csv.DictReader(StringIO(csv_data)))
    if not rows:
        return None

    # Return the most recent close price
    return float(rows[-1]["close"])
