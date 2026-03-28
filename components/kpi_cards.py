"""Top KPI summary row."""
import pandas as pd
import streamlit as st

from data.loader import COL_GROSS_VALUE, COL_ORDER_ID, COL_CUSTOMER_ID, COL_ITEM_ID
from utils.formatting import fmt_currency, fmt_number


def render_kpi_row(data: dict[str, pd.DataFrame]) -> None:
    """Render 4 headline KPI metric cards.

    Args:
        data: Filtered DataFrames.
    """
    df = data["orders"]

    total_revenue     = df[COL_GROSS_VALUE].sum() if COL_GROSS_VALUE in df.columns else 0.0
    total_orders      = df[COL_ORDER_ID].nunique() if COL_ORDER_ID in df.columns else 0
    total_items       = df[COL_ITEM_ID].nunique() if COL_ITEM_ID in df.columns else len(df)
    unique_customers  = df[COL_CUSTOMER_ID].nunique() if COL_CUSTOMER_ID in df.columns else 0
    avg_order_value   = (total_revenue / total_orders) if total_orders > 0 else 0.0

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.metric("💰 Total Revenue", fmt_currency(total_revenue))
    with c2:
        st.metric("🛒 Total Orders", fmt_number(total_orders))
    with c3:
        st.metric("📦 Total Items Sold", fmt_number(total_items))
    with c4:
        st.metric("👤 Unique Customers", fmt_number(unique_customers))
    with c5:
        st.metric("📈 Avg Order Value", fmt_currency(avg_order_value))