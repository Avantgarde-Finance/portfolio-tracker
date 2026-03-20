import asyncio
import os
import logging

import asyncpg
from dotenv import load_dotenv

from constants import CHAIN_ID_TO_NAME

load_dotenv()
logger = logging.getLogger(__name__)


class Database:
    def __init__(self):
        self.pool = None

    async def connect(self):
        if self.pool is None:
            self.pool = await asyncpg.create_pool(
                host=os.getenv("DB_HOST", "localhost"),
                port=int(os.getenv("DB_PORT", "5432")),
                database=os.getenv("DB_NAME", "holdings_data"),
                user=os.getenv("DB_USER", "postgres"),
                password=os.getenv("DB_PASSWORD", ""),
                min_size=1,
                max_size=5,
            )

    async def disconnect(self):
        if self.pool:
            await self.pool.close()
            self.pool = None

    async def fetch(self, query: str, *args):
        await self.connect()
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)

    async def fetchrow(self, query: str, *args):
        await self.connect()
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, *args)

    async def fetchval(self, query: str, *args):
        await self.connect()
        async with self.pool.acquire() as conn:
            return await conn.fetchval(query, *args)


def _run_in_thread(fn):
    """Run an async function in a new thread with its own event loop.

    This avoids 'Event loop is closed' errors when Streamlit's loop
    conflicts with asyncio.run().
    """
    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        return executor.submit(asyncio.run, fn()).result()


async def _fetch_tokens_for_scanning() -> dict:
    """Query token_universe for tokens on supported chains, grouped by chain name."""
    db = Database()
    try:
        chain_ids = list(CHAIN_ID_TO_NAME.keys())
        rows = await db.fetch(
            """
            SELECT chain_id, symbol, token_address, decimals, coingecko_id, price_source
            FROM holdings_data.token_universe
            WHERE chain_id = ANY($1::int[])
            ORDER BY chain_id, symbol
            """,
            chain_ids,
        )

        result = {}
        for row in rows:
            chain_name = CHAIN_ID_TO_NAME.get(row["chain_id"])
            if not chain_name:
                continue
            if chain_name not in result:
                result[chain_name] = {}
            result[chain_name][row["symbol"]] = {
                "address": row["token_address"],
                "decimals": row["decimals"],
                "coingecko_id": row["coingecko_id"],
                "price_source": row["price_source"],
            }

        return result
    finally:
        await db.disconnect()


def get_tokens_for_scanning_sync() -> dict:
    return _run_in_thread(_fetch_tokens_for_scanning)
