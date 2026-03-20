import streamlit as st

st.set_page_config(
    page_title="Cross-Chain Portfolio Tracker",
    page_icon="",
    layout="wide"
)

# Custom CSS (purplish blue theme)
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        min-height: 100vh;
    }

    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
    }

    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 6px 12px rgba(99, 102, 241, 0.08);
        border: 1px solid #c7d2fe;
        border-left: 4px solid #6366f1;
        margin: 0.8rem 0;
        transition: all 0.3s ease;
    }

    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(99, 102, 241, 0.12);
    }

    .portfolio-header {
        background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
        color: white;
        padding: 2.5rem;
        border-radius: 18px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 8px 24px rgba(99, 102, 241, 0.15);
        border: 1px solid #818cf8;
    }

    .portfolio-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    .portfolio-header p {
        margin: 0.5rem 0 0 0;
        opacity: 0.95;
        font-size: 1.1rem;
    }

    .section-header {
        background: linear-gradient(135deg, #818cf8 0%, #6366f1 100%);
        color: #1e1b4b;
        padding: 1.2rem;
        border-radius: 12px;
        margin: 1.5rem 0;
        text-align: center;
        font-weight: 600;
        box-shadow: 0 4px 8px rgba(99, 102, 241, 0.1);
        border: 1px solid #a5b4fc;
    }

    .chain-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 0.2rem;
    }

    .chain-arbitrum {
        background: linear-gradient(135deg, #28a0f0 0%, #1e88e5 100%);
        color: white;
    }

    .chain-ethereum {
        background: linear-gradient(135deg, #627eea 0%, #5368d6 100%);
        color: white;
    }

    .chain-base {
        background: linear-gradient(135deg, #0052ff 0%, #003bbf 100%);
        color: white;
    }

    .chain-optimism {
        background: linear-gradient(135deg, #ff0420 0%, #cc0319 100%);
        color: white;
    }

    .chain-hyperliquid {
        background: linear-gradient(135deg, #00d4ff 0%, #00a8cc 100%);
        color: white;
    }

    .risk-critical {
        background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
        color: white;
        padding: 1.2rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 4px 8px rgba(220, 38, 38, 0.2);
        border: 1px solid #f87171;
    }

    .risk-high {
        background: linear-gradient(135deg, #ea580c 0%, #c2410c 100%);
        color: white;
        padding: 1.2rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 4px 8px rgba(234, 88, 12, 0.2);
        border: 1px solid #fb923c;
    }

    .risk-moderate {
        background: linear-gradient(135deg, #eab308 0%, #ca8a04 100%);
        color: white;
        padding: 1.2rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 4px 8px rgba(234, 179, 8, 0.2);
        border: 1px solid #fbbf24;
    }

    .risk-safe {
        background: linear-gradient(135deg, #059669 0%, #047857 100%);
        color: white;
        padding: 1.2rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 4px 8px rgba(5, 150, 105, 0.2);
        border: 1px solid #34d399;
    }

    .stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
        color: white;
        border: none;
        border-radius: 28px;
        padding: 0.8rem 2.5rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 8px rgba(99, 102, 241, 0.2);
        border: 1px solid #818cf8;
    }

    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 16px rgba(99, 102, 241, 0.3);
        background: linear-gradient(135deg, #4f46e5 0%, #4338ca 100%);
    }
</style>
""", unsafe_allow_html=True)

pg = st.navigation([
    st.Page("pages/0_Portfolio_Scanner.py", title="Portfolio Scanner", default=True),
])
pg.run()
