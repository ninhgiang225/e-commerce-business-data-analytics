import pandas as pd
import streamlit as st
from data.loader import load_data
from components import overview, orders, products, customers, promo_analysis

st.set_page_config(
    page_title="E-Commerce Analytics",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; }

    .block-container { padding-top: 1.8rem; padding-bottom: 1.2rem; }

    div[data-testid="stMetric"] {
        background: #F7FAFC;
        border-radius: 8px;
        padding: 14px 18px;
        border-top: 3px solid #2BBFB3;
    }
    div[data-testid="stMetricLabel"] p {
        font-size: 0.80rem; font-weight: 600;
        text-transform: uppercase; letter-spacing: 0.06em;
        color: #4A5568;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.55rem; font-weight: 700; color: #1A202C;
    }

    .insight-box {
        background: #EBF8FF;
        border-left: 4px solid #2BBFB3;
        padding: 12px 16px; border-radius: 0 8px 8px 0;
        font-size: 0.90rem; color: #1A202C;
        line-height: 1.7; margin: 10px 0;
    }
    .warn-box {
        background: #FFFBEA;
        border-left: 4px solid #F5A623;
        padding: 12px 16px; border-radius: 0 8px 8px 0;
        font-size: 0.90rem; color: #1A202C;
        line-height: 1.7; margin: 10px 0;
    }
    .section-header {
        font-size: 0.75rem; font-weight: 700;
        letter-spacing: 0.10em; text-transform: uppercase;
        color: #4A5568; margin-bottom: 8px;
    }
    .modebar-container { display: none !important; }
</style>
""", unsafe_allow_html=True)

# ── Load data ─────────────────────────────────────────────────────────────────
df = load_data()

with st.sidebar:
    st.markdown("## E-Commerce")
    st.markdown("##### Analytics Dashboard")
    st.markdown("---")

    page = st.radio(
        "Navigate",
        [
            "Overview",
            "Order Analytics",
            "Product & Brand",
            "Customer Analysis",
            "Promo Insight",
        ],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown('<p class="section-header">Filters</p>', unsafe_allow_html=True)

    all_brands      = sorted(df["brand"].dropna().unique())
    selected_brands = st.multiselect("Brand", all_brands, default=all_brands)

    date_min   = df["order_date"].min().date()
    date_max   = df["order_date"].max().date()
    date_range = st.date_input(
        "Date Range", value=(date_min, date_max),
        min_value=date_min, max_value=date_max,
    )

    st.markdown("---")
    st.markdown("""
    <div class="warn-box">
        <b>Data Quality Note</b><br>
        Brand 2 and Brand 3 bundle a free <b>Category 8</b> item per order.
        92 zero-value rows are <b>excluded from revenue metrics</b>.
    </div>
    """, unsafe_allow_html=True)

# ── Filter ────────────────────────────────────────────────────────────────────
if len(date_range) == 2:
    start_date, end_date = date_range
    filtered = df[
        df["brand"].isin(selected_brands) &
        (df["order_date"] >= pd.Timestamp(start_date)) &
        (df["order_date"] <= pd.Timestamp(end_date))
    ].copy()
else:
    filtered = df[df["brand"].isin(selected_brands)].copy()

revenue_df = filtered[filtered["gross_item_value"] > 0].copy()

# ── Route ─────────────────────────────────────────────────────────────────────
if   page == "Overview":          overview.render(filtered, revenue_df)
elif page == "Order Analytics":   orders.render(filtered, revenue_df)
elif page == "Product & Brand":   products.render(filtered, revenue_df)
elif page == "Customer Analysis": customers.render(filtered, revenue_df)
elif page == "Promo Insight":     promo_analysis.render(df, filtered)