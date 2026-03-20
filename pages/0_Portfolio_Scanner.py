import streamlit as st
from decimal import Decimal

from cache_utils import get_cached_tokens_for_scanning
from scanners import MultiChainScanner, HYPERLIQUID_AVAILABLE
from display import display_chain_badge, display_aave_positions, display_hyperliquid_positions, display_wallet_tokens
from constants import DEFAULT_RPC_URLS

# Chain display config: (key, emoji, label)
CHAIN_DISPLAY = [
    ('Ethereum', '🔵', 'Ethereum Token Balances'),
    ('Arbitrum', '🔷', 'Arbitrum Token Balances'),
    ('Base', '🟢', 'Base Token Balances'),
    ('Optimism', '🔴', 'Optimism Token Balances'),
]


def page():
    st.markdown(
        '<div class="portfolio-header">'
        '<h1>Multi-Chain Portfolio Tracker</h1>'
        '<p>Track your positions across Ethereum, Arbitrum, Base, Optimism, Aave, and Hyperliquid</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    # Sidebar configuration
    st.sidebar.header("Configuration")

    rpc_urls = {}
    for chain_name, default_url in DEFAULT_RPC_URLS.items():
        rpc_urls[chain_name] = st.sidebar.text_input(
            f"{chain_name} RPC URL",
            value=default_url,
            help=f"RPC endpoint for {chain_name}",
        )

    user_address = st.sidebar.text_input(
        "Wallet Address",
        value="",
        help="Enter any Ethereum address to scan",
    )

    hl_status = "✅ Available" if HYPERLIQUID_AVAILABLE else "❌ Not installed"
    st.sidebar.write(f"Hyperliquid SDK: {hl_status}")
    st.sidebar.success("✅ CoinGecko Pro API")

    if st.sidebar.button("🔍 Scan Portfolio", type="primary"):
        if not user_address:
            st.error("Please enter a wallet address")
            return

        # Load token data from DB (falls back to hardcoded)
        token_data = get_cached_tokens_for_scanning()

        scanner = MultiChainScanner(
            token_data=token_data,
            rpc_urls=rpc_urls,
        )

        portfolio = scanner.scan_full_portfolio(user_address)

        # --- Display results ---
        st.markdown("## Portfolio Overview")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(
                f'<div class="metric-card"><h4>Wallet</h4>'
                f'<p>{user_address[:10]}...{user_address[-8:]}</p></div>',
                unsafe_allow_html=True,
            )
        with col2:
            st.markdown(
                f'<div class="metric-card"><h4>Total Portfolio Value</h4>'
                f'<h3>${portfolio["total_usd"]:,.2f}</h3></div>',
                unsafe_allow_html=True,
            )
        with col3:
            active_sources = sum(
                1 for key, val in portfolio.items()
                if isinstance(val, list) and len(val) > 0
            )
            st.markdown(
                f'<div class="metric-card"><h4>Active Chains/Protocols</h4>'
                f'<h3>{active_sources}</h3></div>',
                unsafe_allow_html=True,
            )

        st.markdown("---")

        # Native ETH balances
        if portfolio['eth_balances']:
            st.markdown('<div class="section-header"><h3>Native ETH Balances</h3></div>', unsafe_allow_html=True)
            for pos in portfolio['eth_balances']:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(display_chain_badge(pos.chain), unsafe_allow_html=True)
                with col2:
                    st.metric("Amount", f"{pos.amount:.6f} ETH")
                with col3:
                    st.metric("USD Value", f"${pos.usd_value:,.2f}")

        # Token balances per chain
        for chain_name, emoji, label in CHAIN_DISPLAY:
            key = f'{chain_name.lower()}_tokens'
            if portfolio.get(key):
                display_wallet_tokens(portfolio[key], f"{emoji} {label}")

        # Aave positions
        if portfolio.get('aave_ethereum') or portfolio.get('aave_eth_health'):
            display_aave_positions(portfolio['aave_ethereum'], portfolio['aave_eth_health'], 'Ethereum')

        if portfolio.get('aave_arbitrum') or portfolio.get('aave_arb_health'):
            display_aave_positions(portfolio['aave_arbitrum'], portfolio['aave_arb_health'], 'Arbitrum')

        # Hyperliquid positions
        if portfolio.get('hyperliquid'):
            display_hyperliquid_positions(portfolio['hyperliquid'])

        # Scan summary
        st.markdown("---")
        st.markdown("### Scan Summary")

        summary_items = []
        if portfolio['eth_balances']:
            summary_items.append(f"✅ Native ETH on {len(portfolio['eth_balances'])} chain(s)")

        for chain_name, _, _ in CHAIN_DISPLAY:
            key = f'{chain_name.lower()}_tokens'
            tokens = portfolio.get(key, [])
            if tokens:
                summary_items.append(f"✅ {len(tokens)} token(s) on {chain_name}")

        for chain_key in ('ethereum', 'arbitrum'):
            aave_key = f'aave_{chain_key}'
            if portfolio.get(aave_key):
                summary_items.append(f"✅ Aave positions on {chain_key.capitalize()} ({len(portfolio[aave_key])} asset(s))")

        if portfolio.get('hyperliquid'):
            summary_items.append(f"✅ {len(portfolio['hyperliquid'])} Hyperliquid position(s)")

        if not summary_items:
            st.info("No positions found on any supported chain or protocol. Make sure the address is correct!")
        else:
            for item in summary_items:
                st.markdown(item)

        st.markdown("---")
        st.markdown(
            '<div style="text-align: center; color: #6366f1; padding: 2rem;">'
            'Portfolio scan complete!</div>',
            unsafe_allow_html=True,
        )


page()
