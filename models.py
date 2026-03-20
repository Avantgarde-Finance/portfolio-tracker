from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


@dataclass
class AssetPosition:
    symbol: str
    amount: Decimal
    usd_value: Decimal
    source: str
    chain: str = "Unknown"
    share_price: Optional[Decimal] = None
    apy: Optional[Decimal] = None


@dataclass
class AavePosition:
    chain: str
    asset_symbol: str
    asset_address: str
    supplied: Decimal
    borrowed: Decimal
    supplied_usd: Decimal
    borrowed_usd: Decimal
    supply_apy: Decimal
    borrow_apy: Decimal
    used_as_collateral: bool


@dataclass
class AaveAccountHealth:
    chain: str
    total_collateral_usd: Decimal
    total_debt_usd: Decimal
    available_borrows_usd: Decimal
    health_factor: Decimal
    ltv: Decimal
    liquidation_threshold: Decimal


@dataclass
class HyperliquidPosition:
    asset: str
    side: str
    size: Decimal
    entry_price: Decimal
    mark_price: Decimal
    unrealized_pnl: Decimal
    position_value_usd: Decimal
    leverage: Decimal
