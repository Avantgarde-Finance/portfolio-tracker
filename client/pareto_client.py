"""Pareto client for current tranche token prices via on-chain calls."""
import json
from pathlib import Path
from typing import Optional

import streamlit as st
from web3 import Web3

ABI_DIR = Path(__file__).parent.parent / "abi"

with open(ABI_DIR / "pareto_token.json") as f:
    PARETO_TOKEN_ABI = json.load(f)

with open(ABI_DIR / "pareto_vault.json") as f:
    PARETO_VAULT_ABI = json.load(f)


@st.cache_data(ttl=300)
def fetch_pareto_price(token_address: str, chain_id: int, rpc_url: str) -> Optional[float]:
    """Get virtual price for a Pareto tranche token. Cached 5 min.

    Flow:
        1. token.minter() → vault address
        2. vault.virtualPrice(token_address) → price in underlying (assumed USD)
    """
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    if not w3.is_connected():
        return None

    token_addr = Web3.to_checksum_address(token_address)
    token_contract = w3.eth.contract(address=token_addr, abi=PARETO_TOKEN_ABI)

    vault_address = token_contract.functions.minter().call()
    vault_contract = w3.eth.contract(address=Web3.to_checksum_address(vault_address), abi=PARETO_VAULT_ABI)

    raw_price = vault_contract.functions.priceAA().call()
    print(f"[Pareto] {token_address} raw priceAA={raw_price}")
    # priceAA returns price scaled by 1e6 (USDC decimals)
    return float(raw_price) / 1e6
