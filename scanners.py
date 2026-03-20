import streamlit as st
from web3 import Web3
from decimal import Decimal
from typing import Dict, List, Optional, Tuple

from models import AssetPosition, AavePosition, AaveAccountHealth, HyperliquidPosition
from constants import (
    AAVE_V3_CONTRACTS,
    AAVE_POOL_ABI,
    AAVE_POOL_DATA_PROVIDER_ABI,
    ERC20_ABI,
)

# Hyperliquid SDK imports
try:
    from hyperliquid.info import Info
    from hyperliquid.utils import constants as hl_constants
    HYPERLIQUID_AVAILABLE = True
except ImportError:
    HYPERLIQUID_AVAILABLE = False


from client.coingecko_client import fetch_coingecko_prices
from client.morpho_client import fetch_morpho_v1_price, fetch_morpho_v2_price
from client.pendle_client import fetch_pendle_price
from client.pareto_client import fetch_pareto_price
from constants import CHAIN_ID_TO_NAME, CHAIN_NAME_TO_ID, DEFAULT_RPC_URLS


class PriceResolver:
    """Fetches prices from the appropriate source based on price_source field.

    price_source mapping:
        1 = CoinGecko   (batched /simple/price)
        2 = Morpho V1   (per-token GraphQL)
        3 = Pendle       (per-token OHLCV)
        4 = Morpho V2   (per-token GraphQL)
        6 = Pareto       (on-chain: minter() → virtualPrice())
    """

    def __init__(self, coingecko_id_map: Dict[str, str], rpc_urls: Dict[str, str] = None):
        self.cg_map = coingecko_id_map
        self.cg_map.setdefault('ETH', 'ethereum')
        self.rpc_urls = rpc_urls or DEFAULT_RPC_URLS
        self.price_cache: Dict[str, float] = {}

    def fetch_prices(self, token_data: Dict[str, Dict], held_symbols_by_chain: Dict[str, set]):
        """Fetch prices for all held tokens, dispatching to the right source.

        Args:
            token_data: {chain_name: {symbol: {address, decimals, coingecko_id, price_source}}}
            held_symbols_by_chain: {chain_name: {symbol, ...}} — only tokens with balance > 0
        """
        cg_symbols = set()
        other_fetches = []  # [(symbol, price_source, address, chain_id, chain_name)]

        for chain_name, symbols in held_symbols_by_chain.items():
            chain_tokens = token_data.get(chain_name, {})
            chain_id = CHAIN_NAME_TO_ID.get(chain_name)
            for symbol in symbols:
                info = chain_tokens.get(symbol, {})
                ps = info.get('price_source')
                if ps == 1:
                    cg_symbols.add(symbol)
                elif ps in (2, 3, 4, 6) and chain_id:
                    other_fetches.append((symbol, ps, info['address'], chain_id, chain_name))

        # Always price native ETH via CoinGecko
        cg_symbols.add('ETH')

        # Batch CoinGecko
        if cg_symbols:
            to_fetch = {s: self.cg_map[s] for s in cg_symbols if s in self.cg_map}
            if to_fetch:
                coin_ids = ','.join(sorted(set(to_fetch.values())))
                try:
                    cg_prices = fetch_coingecko_prices(coin_ids)
                    for symbol, coin_id in to_fetch.items():
                        if coin_id in cg_prices:
                            self.price_cache[symbol] = float(cg_prices[coin_id])
                except Exception:
                    pass

        # Per-token sources
        source_names = {2: 'Morpho V1', 3: 'Pendle', 4: 'Morpho V2', 6: 'Pareto'}
        for symbol, ps, address, chain_id, chain_name in other_fetches:
            try:
                price = None
                if ps == 2:
                    price = fetch_morpho_v1_price(address, chain_id)
                elif ps == 4:
                    price = fetch_morpho_v2_price(address, chain_id)
                elif ps == 3:
                    price = fetch_pendle_price(address, chain_id)
                elif ps == 6:
                    rpc_url = self.rpc_urls.get(chain_name, '')
                    if rpc_url:
                        price = fetch_pareto_price(address, chain_id, rpc_url)
                    else:
                        continue
                else:
                    continue
                if price is not None:
                    self.price_cache[symbol] = price
                else:
                    st.warning(f"No price returned for {symbol} from {source_names.get(ps, ps)} (address={address}, chain={chain_id})")
            except Exception as e:
                st.warning(f"Failed to fetch price for {symbol} from {source_names.get(ps, ps)}: {e}")

    def get_price(self, symbol: str) -> float:
        return self.price_cache.get(symbol, 0)


class HyperliquidScanner:
    """Hyperliquid positions scanner"""

    def __init__(self):
        self.available = HYPERLIQUID_AVAILABLE
        if self.available:
            try:
                self.info = Info(hl_constants.MAINNET_API_URL, skip_ws=True)
            except Exception as e:
                st.warning(f"Failed to initialize Hyperliquid: {e}")
                self.available = False
                self.info = None
        else:
            self.info = None

    def get_user_positions(self, address: str) -> List[HyperliquidPosition]:
        if not self.available or not self.info:
            return []

        try:
            user_state = self.info.user_state(address)

            if not user_state or 'assetPositions' not in user_state:
                return []

            positions = []
            for pos_data in user_state['assetPositions']:
                try:
                    position = pos_data.get('position', {})

                    size = float(position.get('szi', 0))
                    if size == 0:
                        continue

                    entry_price = float(position.get('entryPx', 0))
                    position_value = float(position.get('positionValue', 0))
                    unrealized_pnl = float(position.get('unrealizedPnl', 0))

                    mark_price = position_value / abs(size) if size != 0 else 0

                    leverage_data = position.get('leverage', {})
                    leverage = float(leverage_data.get('value', 0)) if leverage_data else 1.0

                    positions.append(HyperliquidPosition(
                        asset=position.get('coin', 'Unknown'),
                        side='LONG' if size > 0 else 'SHORT',
                        size=Decimal(str(abs(size))),
                        entry_price=Decimal(str(entry_price)),
                        mark_price=Decimal(str(mark_price)),
                        unrealized_pnl=Decimal(str(unrealized_pnl)),
                        position_value_usd=Decimal(str(abs(position_value))),
                        leverage=Decimal(str(leverage))
                    ))
                except Exception:
                    continue

            return positions

        except Exception as e:
            st.warning(f"Failed to fetch Hyperliquid positions: {e}")
            return []


class AaveScanner:
    """Aave V3 positions scanner"""

    def __init__(self, chain: str, rpc_url: str, price_source):
        self.chain = chain
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.price_source = price_source

        if not self.w3.is_connected():
            st.warning(f"Failed to connect to {chain} RPC")
            return

        self.contracts = AAVE_V3_CONTRACTS.get(chain, {})
        if not self.contracts:
            st.warning(f"No Aave contracts configured for {chain}")

    def _get_contract(self, address: str, abi: list):
        return self.w3.eth.contract(address=Web3.to_checksum_address(address), abi=abi)

    def get_user_positions(self, user_address: str) -> Tuple[List[AavePosition], Optional[AaveAccountHealth]]:
        if not self.w3.is_connected() or not self.contracts:
            return [], None

        try:
            user_address = Web3.to_checksum_address(user_address)

            data_provider = self._get_contract(
                self.contracts['pool_data_provider'],
                AAVE_POOL_DATA_PROVIDER_ABI
            )

            pool = self._get_contract(
                self.contracts['pool'],
                AAVE_POOL_ABI
            )

            health = None
            try:
                account_data = pool.functions.getUserAccountData(user_address).call()

                if account_data[0] > 0 or account_data[1] > 0:
                    health = AaveAccountHealth(
                        chain=self.chain,
                        total_collateral_usd=Decimal(str(account_data[0])) / Decimal('1e8'),
                        total_debt_usd=Decimal(str(account_data[1])) / Decimal('1e8'),
                        available_borrows_usd=Decimal(str(account_data[2])) / Decimal('1e8'),
                        health_factor=Decimal(str(account_data[5])) / Decimal('1e18') if account_data[5] > 0 else Decimal('0'),
                        ltv=Decimal(str(account_data[4])) / Decimal('100'),
                        liquidation_threshold=Decimal(str(account_data[3])) / Decimal('100')
                    )
            except Exception:
                pass

            positions = []
            try:
                reserves_data = data_provider.functions.getUserReservesData(user_address).call()

                for reserve in reserves_data:
                    try:
                        underlying_asset = reserve[0]
                        atoken_balance_scaled = reserve[1]
                        used_as_collateral = reserve[2]
                        variable_debt_scaled = reserve[4]
                        stable_debt = reserve[5]

                        if atoken_balance_scaled == 0 and variable_debt_scaled == 0 and stable_debt == 0:
                            continue

                        asset_contract = self._get_contract(underlying_asset, ERC20_ABI)
                        symbol = asset_contract.functions.symbol().call()
                        decimals = asset_contract.functions.decimals().call()

                        reserve_data = data_provider.functions.getReserveData(underlying_asset).call()

                        liquidity_index = reserve_data[9]
                        variable_borrow_index = reserve_data[10]

                        supplied = Decimal(str(atoken_balance_scaled * liquidity_index // (10**27))) / Decimal(f'1e{decimals}')
                        borrowed = Decimal(str(variable_debt_scaled * variable_borrow_index // (10**27))) / Decimal(f'1e{decimals}')

                        price = Decimal(str(self.price_source.get_price(symbol)))

                        supply_apy = Decimal(str(reserve_data[5])) / Decimal('1e25')
                        borrow_apy = Decimal(str(reserve_data[6])) / Decimal('1e25')

                        positions.append(AavePosition(
                            chain=self.chain,
                            asset_symbol=symbol,
                            asset_address=underlying_asset,
                            supplied=supplied,
                            borrowed=borrowed,
                            supplied_usd=supplied * price,
                            borrowed_usd=borrowed * price,
                            supply_apy=supply_apy,
                            borrow_apy=borrow_apy,
                            used_as_collateral=used_as_collateral
                        ))

                    except Exception:
                        continue

            except Exception:
                pass

            return positions, health

        except Exception as e:
            if "execution reverted" not in str(e):
                st.warning(f"Error checking Aave on {self.chain}: {e}")
            return [], None


class MultiChainScanner:
    """Multi-chain portfolio scanner"""

    # Chains that support native ETH balance checks
    ETH_BALANCE_CHAINS = {'Ethereum', 'Arbitrum', 'Base', 'Optimism'}
    # Chains that have Aave V3 deployments we scan
    AAVE_CHAINS = {'Ethereum', 'Arbitrum'}

    def __init__(
        self,
        token_data: Dict[str, Dict],
        rpc_urls: Dict[str, str],
    ):
        self.token_data = token_data
        # Build coingecko_id map from token_data
        cg_map = {}
        for tokens in token_data.values():
            for symbol, info in tokens.items():
                if info.get('coingecko_id') and info.get('price_source') == 1:
                    cg_map[symbol] = info['coingecko_id']
        self.price_resolver = PriceResolver(coingecko_id_map=cg_map, rpc_urls=rpc_urls)

        # Create Web3 instances for each chain with an RPC URL
        self.w3_instances: Dict[str, Web3] = {}
        for chain_name, rpc_url in rpc_urls.items():
            if rpc_url:
                self.w3_instances[chain_name] = Web3(Web3.HTTPProvider(rpc_url))

        # Initialize Aave scanners (Ethereum + Arbitrum only)
        self.aave_scanners: Dict[str, AaveScanner] = {}
        for chain in self.AAVE_CHAINS:
            chain_key = chain.lower()
            if chain in rpc_urls and rpc_urls[chain]:
                self.aave_scanners[chain_key] = AaveScanner(chain_key, rpc_urls[chain], self.price_resolver)

        # Hyperliquid
        self.hyperliquid = HyperliquidScanner()

    def get_asset_price_usd(self, symbol: str) -> float:
        return self.price_resolver.get_price(symbol)

    def _format_token_list(self, tokens: Dict) -> Dict[str, Dict]:
        """Strip to {SYMBOL: {address, decimals, price_source}}."""
        return {
            symbol: {
                'address': info['address'],
                'decimals': info['decimals'],
                'price_source': info.get('price_source'),
            }
            for symbol, info in tokens.items()
        }

    def get_eth_balances_no_price(self, address: str) -> List[AssetPosition]:
        """Check native ETH balances on all chains. USD value set to 0, filled later."""
        positions = []
        address = Web3.to_checksum_address(address)

        for chain_name in self.ETH_BALANCE_CHAINS:
            w3 = self.w3_instances.get(chain_name)
            if not w3 or not w3.is_connected():
                continue
            try:
                balance_wei = w3.eth.get_balance(address)
                balance_eth = Decimal(str(balance_wei)) / Decimal('1e18')
                if balance_eth > 0:
                    positions.append(AssetPosition(
                        symbol='ETH',
                        amount=balance_eth,
                        usd_value=Decimal('0'),
                        source='Wallet',
                        chain=chain_name,
                    ))
            except Exception as e:
                st.warning(f"Failed to get ETH balance on {chain_name}: {e}")

        return positions

    def _check_single_balance(self, w3, address: str, symbol: str, config: Dict) -> Optional[tuple]:
        """Check balance for a single token. Returns (symbol, balance, decimals) or None."""
        try:
            token_contract = w3.eth.contract(
                address=Web3.to_checksum_address(config['address']),
                abi=ERC20_ABI
            )
            balance = token_contract.functions.balanceOf(address).call()
            if balance > 0:
                return (symbol, balance, config.get('decimals', 18))
        except Exception:
            pass
        return None

    def get_token_balances_no_price(self, address: str, chain: str, token_list: Dict[str, Dict]) -> List[AssetPosition]:
        """Check ERC-20 balances. USD value set to 0, filled later."""
        from concurrent.futures import ThreadPoolExecutor, as_completed

        w3 = self.w3_instances.get(chain)

        if not w3 or not w3.is_connected():
            return []

        address = Web3.to_checksum_address(address)
        positions = []
        total = len(token_list)
        done = 0

        log_placeholder = st.empty()

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {
                executor.submit(self._check_single_balance, w3, address, symbol, config): symbol
                for symbol, config in token_list.items()
            }

            for future in as_completed(futures):
                done += 1
                symbol = futures[future]
                log_placeholder.text(f"  [{done}/{total}] Checked {symbol}...")
                result = future.result()
                if result:
                    sym, balance, decimals = result
                    amount = Decimal(str(balance)) / Decimal(f'1e{decimals}')
                    positions.append(AssetPosition(
                        symbol=sym,
                        amount=amount,
                        usd_value=Decimal('0'),
                        source='Wallet',
                        chain=chain
                    ))

        log_placeholder.empty()
        return positions

    def _collect_held_symbols_by_chain(self, portfolio: Dict, chain_token_keys: Dict) -> Dict[str, set]:
        """Collect symbols with non-zero balances, grouped by chain."""
        result = {}
        for chain_name in self.token_data:
            key = chain_token_keys.get(chain_name, '')
            symbols = {pos.symbol for pos in portfolio.get(key, [])}
            if symbols:
                result[chain_name] = symbols
        return result

    def scan_full_portfolio(self, address: str) -> Dict:
        portfolio = {
            'eth_balances': [],
            'aave_ethereum': [],
            'aave_arbitrum': [],
            'aave_eth_health': None,
            'aave_arb_health': None,
            'hyperliquid': [],
            'total_usd': Decimal('0'),
        }

        # Add keys for each chain's tokens
        chain_token_keys = {}
        for chain_name in self.token_data:
            key = f'{chain_name.lower()}_tokens'
            portfolio[key] = []
            chain_token_keys[chain_name] = key

        # Steps: ETH + chains + price fetch + aave scanners + hyperliquid
        num_steps = 2 + len(self.token_data) + len(self.aave_scanners) + 1
        progress = st.progress(0)
        step = 0

        # 1. Check ETH balances (no price yet)
        step += 1
        progress.progress(step / num_steps)
        with st.spinner("Checking ETH balances..."):
            portfolio['eth_balances'] = self.get_eth_balances_no_price(address)

        # 2. Check token balances (no price yet)
        for chain_name, tokens in self.token_data.items():
            step += 1
            progress.progress(step / num_steps)
            with st.spinner(f"Scanning {chain_name} tokens..."):
                token_list = self._format_token_list(tokens)
                key = chain_token_keys[chain_name]
                portfolio[key] = self.get_token_balances_no_price(address, chain_name, token_list)

        # 3. Fetch prices for non-zero balances (dispatched by price_source)
        step += 1
        progress.progress(step / num_steps)
        held = self._collect_held_symbols_by_chain(portfolio, chain_token_keys)
        total_held = sum(len(s) for s in held.values())
        if total_held > 0 or portfolio['eth_balances']:
            with st.spinner(f"Fetching prices for {total_held + bool(portfolio['eth_balances'])} tokens..."):
                self.price_resolver.fetch_prices(self.token_data, held)
                num_priced = len(self.price_resolver.price_cache)
                if num_priced:
                    st.success(f"Loaded prices for {num_priced} assets")

        # 4. Apply prices to positions
        for pos in portfolio['eth_balances']:
            pos.usd_value = pos.amount * Decimal(str(self.get_asset_price_usd('ETH')))
        for chain_name in self.token_data:
            key = chain_token_keys[chain_name]
            for pos in portfolio[key]:
                pos.usd_value = pos.amount * Decimal(str(self.get_asset_price_usd(pos.symbol)))

        # 5. Aave positions (these fetch their own prices internally)
        for chain_key, scanner in self.aave_scanners.items():
            step += 1
            progress.progress(step / num_steps)
            chain_display = chain_key.capitalize()
            with st.spinner(f"Checking Aave on {chain_display}..."):
                positions, health = scanner.get_user_positions(address)
                portfolio[f'aave_{chain_key}'] = positions
                portfolio[f'aave_{chain_key[:3]}_health'] = health
                if positions:
                    st.success(f"Found {len(positions)} Aave positions on {chain_display}")

        # 6. Hyperliquid
        step += 1
        progress.progress(step / num_steps)
        with st.spinner("Checking Hyperliquid positions..."):
            portfolio['hyperliquid'] = self.hyperliquid.get_user_positions(address)
            if portfolio['hyperliquid']:
                st.success(f"Found {len(portfolio['hyperliquid'])} Hyperliquid positions")

        progress.progress(1.0)

        # Calculate total
        total = Decimal('0')
        for pos in portfolio['eth_balances']:
            total += pos.usd_value
        for chain_name in self.token_data:
            key = chain_token_keys[chain_name]
            for pos in portfolio[key]:
                total += pos.usd_value
        for pos in portfolio.get('aave_ethereum', []):
            total += pos.supplied_usd - pos.borrowed_usd
        for pos in portfolio.get('aave_arbitrum', []):
            total += pos.supplied_usd - pos.borrowed_usd
        for pos in portfolio['hyperliquid']:
            total += pos.unrealized_pnl

        portfolio['total_usd'] = total

        return portfolio
