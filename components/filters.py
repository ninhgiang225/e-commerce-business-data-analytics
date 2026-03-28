"""Sidebar filter widgets."""
import datetime
import pandas as pd
import streamlit as st

from data.loader import COL_BRAND, COL_COUNTRY, COL_ORDER_DATE, COL_PRODUCT_GROUP, COL_STATE


def render_sidebar_filters(data: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """Render sidebar filters and return filtered data dict.

    Args:
        data: Raw DataFrames from load_all_data().

    Returns:
        Same dict with 'orders' filtered by sidebar selections.
    """
    df = data["orders"].copy()

    with st.sidebar:
        st.markdown("## 🔍 Filters")

        # ── Date range ────────────────────────────────────────────────────────
        if COL_ORDER_DATE in df.columns and df[COL_ORDER_DATE].notna().any():
            min_d = df[COL_ORDER_DATE].min().date()
            max_d = df[COL_ORDER_DATE].max().date()
            date_range = st.date_input(
                "📅 Order date range",
                value=(min_d, max_d),
                min_value=min_d,
                max_value=max_d,
                key="filter_date",
            )
            if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
                s, e = date_range
                df = df[(df[COL_ORDER_DATE].dt.date >= s) & (df[COL_ORDER_DATE].dt.date <= e)]

        st.markdown("---")

        # ── State ─────────────────────────────────────────────────────────────
        if COL_STATE in df.columns:
            states = sorted(df[COL_STATE].dropna().unique().tolist())
            sel = st.multiselect("🗺️ State", states, default=states, key="filter_state")
            if sel:
                df = df[df[COL_STATE].isin(sel)]

        # ── Brand ─────────────────────────────────────────────────────────────
        if COL_BRAND in df.columns:
            brands = sorted(df[COL_BRAND].dropna().unique().tolist())
            sel = st.multiselect("🏷️ Brand", brands, default=brands, key="filter_brand")
            if sel:
                df = df[df[COL_BRAND].isin(sel)]

        # ── Product group ─────────────────────────────────────────────────────
        if COL_PRODUCT_GROUP in df.columns:
            groups = sorted(df[COL_PRODUCT_GROUP].dropna().unique().tolist())
            sel = st.multiselect("📦 Product Group", groups, default=groups, key="filter_pg")
            if sel:
                df = df[df[COL_PRODUCT_GROUP].isin(sel)]

        st.markdown("---")
        if st.button("↺ Reset all filters", use_container_width=True):
            for k in [k for k in st.session_state if k.startswith("filter_")]:
                del st.session_state[k]
            st.rerun()

        st.caption(f"{len(df):,} order items shown")

    return {**data, "orders": df}