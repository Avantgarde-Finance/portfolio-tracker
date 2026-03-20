import streamlit as st
import pandas as pd
from decimal import Decimal
from typing import List, Optional

from models import AssetPosition, AavePosition, AaveAccountHealth, HyperliquidPosition


def display_chain_badge(chain: str):
    chain_class = f"chain-{chain.lower()}"
    return f'<span class="{chain_class} chain-badge">{chain}</span>'


def display_aave_positions(positions: List[AavePosition], health: Optional[AaveAccountHealth], chain: str):
    if not positions and not health:
        return

    st.markdown(f'<div class="section-header"><h3>Aave V3 Positions - {chain}</h3></div>', unsafe_allow_html=True)

    if health and health.total_collateral_usd > 0:
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Collateral", f"${health.total_collateral_usd:,.2f}")
        with col2:
            st.metric("Total Debt", f"${health.total_debt_usd:,.2f}")
        with col3:
            st.metric("Available to Borrow", f"${health.available_borrows_usd:,.2f}")
        with col4:
            hf_color = "🟢" if health.health_factor > 2 else "🟡" if health.health_factor > 1.5 else "🔴"
            st.metric("Health Factor", f"{hf_color} {health.health_factor:.2f}")

        if health.health_factor > 0:
            if health.health_factor < 1.1:
                st.markdown('<div class="risk-critical">⚠️ CRITICAL: Health factor below 1.1 - Risk of liquidation!</div>', unsafe_allow_html=True)
            elif health.health_factor < 1.5:
                st.markdown('<div class="risk-high">⚠️ HIGH RISK: Health factor below 1.5 - Monitor closely</div>', unsafe_allow_html=True)
            elif health.health_factor < 2.0:
                st.markdown('<div class="risk-moderate">⚠️ MODERATE: Consider adding collateral for safety</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="risk-safe">✅ HEALTHY: Position is safe</div>', unsafe_allow_html=True)

    if positions:
        position_data = []
        for pos in positions:
            position_data.append({
                'Asset': pos.asset_symbol,
                'Supplied': f"{pos.supplied:.6f}",
                'Supplied USD': f"${pos.supplied_usd:.2f}",
                'Supply APY': f"{pos.supply_apy:.2f}%",
                'Borrowed': f"{pos.borrowed:.6f}",
                'Borrowed USD': f"${pos.borrowed_usd:.2f}",
                'Borrow APY': f"{pos.borrow_apy:.2f}%",
                'Collateral': '✅' if pos.used_as_collateral else '❌'
            })

        df = pd.DataFrame(position_data)
        st.dataframe(df, use_container_width=True, hide_index=True)


def display_hyperliquid_positions(positions: List[HyperliquidPosition]):
    if not positions:
        return

    st.markdown('<div class="section-header"><h3>Hyperliquid Positions</h3></div>', unsafe_allow_html=True)

    position_data = []
    total_pnl = Decimal('0')
    total_value = Decimal('0')

    for pos in positions:
        position_data.append({
            'Asset': pos.asset,
            'Side': pos.side,
            'Size': f"{pos.size:.4f}",
            'Entry Price': f"${pos.entry_price:,.2f}",
            'Mark Price': f"${pos.mark_price:,.2f}",
            'PnL': f"${pos.unrealized_pnl:,.2f}",
            'Value': f"${pos.position_value_usd:,.2f}",
            'Leverage': f"{pos.leverage:.1f}x"
        })
        total_pnl += pos.unrealized_pnl
        total_value += pos.position_value_usd

    df = pd.DataFrame(position_data)
    st.dataframe(df, use_container_width=True, hide_index=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Position Value", f"${total_value:,.2f}")
    with col2:
        pnl_color = "🟢" if total_pnl > 0 else "🔴"
        st.metric("Total Unrealized PnL", f"{pnl_color} ${total_pnl:,.2f}")
    with col3:
        st.metric("Number of Positions", str(len(positions)))


def display_wallet_tokens(positions: List[AssetPosition], title: str):
    if not positions:
        return

    st.markdown(f'<div class="section-header"><h3>{title}</h3></div>', unsafe_allow_html=True)

    position_data = []
    total_usd = Decimal('0')

    for pos in positions:
        position_data.append({
            'Asset': pos.symbol,
            'Chain': pos.chain,
            'Amount': f"{pos.amount:.6f}",
            'USD Value': f"${pos.usd_value:.6f}"
        })
        total_usd += pos.usd_value

    df = pd.DataFrame(position_data)
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.markdown(f'<div class="metric-card"><h4>Total: ${total_usd:,.2f}</h4></div>', unsafe_allow_html=True)
