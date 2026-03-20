import logging

import streamlit as st

from database import get_tokens_for_scanning_sync
from constants import FALLBACK_TOKEN_DATA

logger = logging.getLogger(__name__)


@st.cache_data(ttl=3600)
def get_cached_tokens_for_scanning() -> dict:
    try:
        data = get_tokens_for_scanning_sync()
        if data:
            total = sum(len(v) for v in data.values())
            logger.info(f"Loaded {total} tokens from DB across {len(data)} chains")
            return data
    except Exception as e:
        logger.warning(f"DB unavailable for token data, using fallback: {e}")
    return FALLBACK_TOKEN_DATA
