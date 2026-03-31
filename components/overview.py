import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from utils.charts import base_layout, fmt_currency, fmt_number, PALETTE, TEAL, AMBER, PURPLE


def render(df: pd.DataFrame, revenue_df: pd.DataFrame) -> None:
    st.markdown("## Overview")

    # ── KPIs ──────────────────────────────────────────────────────────────────
    total_revenue   = revenue_df["gross_item_value"].sum()
    total_orders    = revenue_df["order_id"].nunique()
    total_customers = revenue_df["customer_id"].nunique()
    aov             = revenue_df.groupby("order_id")["gross_item_value"].sum().mean()
    avg_item_value  = revenue_df["gross_item_value"].mean()
    avg_basket      = revenue_df.groupby("order_id")["item_id"].count().mean()

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Total Revenue",     fmt_currency(total_revenue))
    c2.metric("Orders",            fmt_number(total_orders))
    c3.metric("Customers",         fmt_number(total_customers))
    c4.metric("AOV",               fmt_currency(aov))
    c5.metric("Avg Item Value",    fmt_currency(avg_item_value))
    c6.metric("Avg Basket Size",   f"{avg_basket:.1f} items")

    st.markdown("---")

    # ── Q1 (swapped here): Daily Order Volume ─────────────────────────────────
    col_a, col_b = st.columns([3, 1])

    with col_a:
        st.markdown('<p class="section-header">Daily Order Volume</p>', unsafe_allow_html=True)
        daily_orders = (
            revenue_df.groupby("order_date")["order_id"]
            .nunique()
            .reset_index()
            .rename(columns={"order_id": "n_orders"})
            .sort_values("order_date")
        )
        daily_orders["rolling_7"] = daily_orders["n_orders"].rolling(7, min_periods=1).mean()

        fig = go.Figure()
        fig.add_bar(
            x=daily_orders["order_date"],
            y=daily_orders["n_orders"],
            marker_color=TEAL,
            opacity=0.75,
            name="Daily Orders",
            hovertemplate="%{x|%b %d}<br><b>%{y} orders</b><extra></extra>",
        )
        fig.add_scatter(
            x=daily_orders["order_date"],
            y=daily_orders["rolling_7"],
            mode="lines",
            line=dict(color=AMBER, width=2, dash="dot"),
            name="7-day avg",
            hovertemplate="%{x|%b %d}<br>7-day avg: <b>%{y:.1f}</b><extra></extra>",
        )
        fig.update_layout(title="Order Volume by Day")
        fig.update_yaxes(title="Number of Orders")
        fig.update_xaxes(title="Date")
        base_layout(fig, height=300)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with col_b:
        st.markdown('<p class="section-header">Revenue by Brand</p>', unsafe_allow_html=True)
        brand_rev = (
            revenue_df.groupby("brand")["gross_item_value"]
            .sum()
            .sort_values(ascending=True)
            .reset_index()
        )
        fig2 = go.Figure(go.Bar(
            x=brand_rev["gross_item_value"],
            y=brand_rev["brand"],
            orientation="h",
            marker_color=TEAL,
            opacity=0.85,
            hovertemplate="%{y}<br><b>$%{x:,.0f}</b><extra></extra>",
        ))
        fig2.update_layout(title="Revenue by Brand")
        fig2.update_xaxes(tickprefix="$", tickformat=",.0f", title="Revenue ($)")
        fig2.update_yaxes(title="")
        base_layout(fig2, height=300)
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

    # ── Revenue by category & state ───────────────────────────────────────────
    col_c, col_d = st.columns(2)

    with col_c:
        st.markdown('<p class="section-header">Revenue by Product Group</p>', unsafe_allow_html=True)
        cat_rev = (
            revenue_df.groupby("product_group")["gross_item_value"]
            .sum()
            .sort_values(ascending=True)
            .reset_index()
        )
        fig3 = go.Figure(go.Bar(
            x=cat_rev["gross_item_value"],
            y=cat_rev["product_group"],
            orientation="h",
            marker_color=PURPLE,
            opacity=0.85,
            hovertemplate="%{y}<br><b>$%{x:,.0f}</b><extra></extra>",
        ))
        fig3.update_layout(title="Revenue by Category")
        fig3.update_xaxes(tickprefix="$", tickformat=",.0f", title="Revenue ($)")
        fig3.update_yaxes(title="")
        base_layout(fig3, height=300)
        st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})

    with col_d:
        st.markdown('<p class="section-header">Top 10 States by Revenue</p>', unsafe_allow_html=True)
        state_rev = (
            revenue_df.groupby("state")["gross_item_value"]
            .sum()
            .sort_values(ascending=False)
            .head(10)
            .sort_values(ascending=True)
            .reset_index()
        )
        fig4 = go.Figure(go.Bar(
            x=state_rev["gross_item_value"],
            y=state_rev["state"],
            orientation="h",
            marker_color=AMBER,
            opacity=0.85,
            hovertemplate="%{y}<br><b>$%{x:,.0f}</b><extra></extra>",
        ))
        fig4.update_layout(title="Top 10 States by Revenue")
        fig4.update_xaxes(tickprefix="$", tickformat=",.0f", title="Revenue ($)")
        fig4.update_yaxes(title="")
        base_layout(fig4, height=300)
        st.plotly_chart(fig4, use_container_width=True, config={"displayModeBar": False})