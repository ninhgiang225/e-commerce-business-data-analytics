"""Chart sections — one function per analyst question."""
from typing import Optional

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import scipy.stats as stats
import streamlit as st

from data.loader import (
    COL_BRAND, COL_COUNTRY, COL_GROSS_VALUE, COL_ORDER_DATE, COL_ORDER_DT,
    COL_ORDER_ID, COL_PRODUCT_GROUP, COL_STATE, COL_CUSTOMER_ID, COL_ITEM_ID,
)
from utils.formatting import PALETTE, CHART_TEMPLATE, fmt_currency, fmt_number

# ── Shared helpers ────────────────────────────────────────────────────────────

def _order_totals(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate item-level rows into order-level totals.

    Args:
        df: Enriched orders DataFrame (item-level).

    Returns:
        DataFrame with one row per order_id and columns:
        order_id, order_date, order_datetime (if present),
        order_value, and any first-occurrence dimension columns.
    """
    agg: dict = {COL_GROSS_VALUE: "sum"}
    extra_cols = [c for c in [COL_ORDER_DATE, COL_ORDER_DT, COL_STATE,
                               COL_BRAND, COL_COUNTRY, COL_CUSTOMER_ID,
                               "day_of_week", "hour_of_day"]
                  if c in df.columns]
    for c in extra_cols:
        agg[c] = "first"

    return (
        df.groupby(COL_ORDER_ID, as_index=False)
          .agg(agg)
          .rename(columns={COL_GROSS_VALUE: "order_value"})
    )


def _base_layout(fig: go.Figure, t: int = 48) -> go.Figure:
    """Apply shared layout tweaks."""
    fig.update_layout(margin=dict(l=0, r=0, t=t, b=0))
    return fig


# ── Q1: Total Order Value by Day ──────────────────────────────────────────────

def render_q1_daily_order_value(data: dict[str, pd.DataFrame]) -> None:
    """Q1 — Plot Total Order Value by day.

    Method: sum gross_item_value per order → sum order values per calendar day.

    Args:
        data: Filtered DataFrames.
    """
    df = data["orders"]

    if COL_ORDER_DATE not in df.columns or COL_GROSS_VALUE not in df.columns:
        st.warning("Need order_date and gross_item_value columns.")
        return

    orders = _order_totals(df)
    daily = (
        orders.groupby(COL_ORDER_DATE)["order_value"]
        .sum()
        .reset_index()
        .rename(columns={COL_ORDER_DATE: "Date", "order_value": "Total Order Value ($)"})
        .sort_values("Date")
    )

    fig = px.bar(
        daily, x="Date", y="Total Order Value ($)",
        title="Total Order Value by Day",
        labels={"Date": "Date", "Total Order Value ($)": "Total Order Value ($)"},
        color="Total Order Value ($)",
        color_continuous_scale=["#BAE6FD", "#0EA5E9", "#0369A1"],
        template=CHART_TEMPLATE,
    )
    fig.update_traces(
        hovertemplate="<b>%{x|%b %d, %Y}</b><br>Total: $%{y:,.0f}<extra></extra>"
    )
    fig.update_layout(
        coloraxis_showscale=False,
        margin=dict(l=0, r=0, t=48, b=0),
        yaxis_tickprefix="$", yaxis_tickformat=",.0f",
    )
    # Overlay 7-day rolling average line
    daily["7-day Avg"] = daily["Total Order Value ($)"].rolling(7, min_periods=1).mean()
    fig.add_trace(go.Scatter(
        x=daily["Date"], y=daily["7-day Avg"],
        mode="lines", name="7-day avg",
        line=dict(color="#F59E0B", width=2, dash="dot"),
    ))
    st.plotly_chart(fig, use_container_width=True)

    peak = daily.loc[daily["Total Order Value ($)"].idxmax()]
    st.markdown(
        f'<div class="insight-box">📌 <b>Peak day:</b> {peak["Date"].strftime("%B %d, %Y")} '
        f'with <b>{fmt_currency(peak["Total Order Value ($)"])}</b> in total order value.</div>',
        unsafe_allow_html=True,
    )


# ── Q2: Average Order Value in January ───────────────────────────────────────

def render_q2_january_aov(data: dict[str, pd.DataFrame]) -> None:
    """Q2 — Average Order Value in January.

    Method: filter to January rows, compute order totals,
    then take the mean of those order totals.

    Args:
        data: Filtered DataFrames.
    """
    df = data["orders"]

    if COL_ORDER_DATE not in df.columns:
        st.warning("Need order_date column.")
        return

    jan_df = df[df[COL_ORDER_DATE].dt.month == 1]

    if jan_df.empty:
        st.info("No January data found in the current filter selection.")
        return

    jan_orders = _order_totals(jan_df)

    # Per-year breakdown in case data spans multiple years
    jan_orders["Year"] = jan_orders[COL_ORDER_DATE].dt.year
    yearly_aov = (
        jan_orders.groupby("Year")["order_value"]
        .mean()
        .reset_index()
        .rename(columns={"order_value": "Avg Order Value ($)"})
    )

    overall_aov = jan_orders["order_value"].mean()
    n_orders    = len(jan_orders)

    col1, col2 = st.columns([1, 2])

    with col1:
        st.metric("January AOV (all years)", fmt_currency(overall_aov))
        st.metric("January Orders", fmt_number(n_orders))
        if len(yearly_aov) > 1:
            for _, row in yearly_aov.iterrows():
                st.metric(f"January {int(row['Year'])} AOV", fmt_currency(row["Avg Order Value ($)"]))

    with col2:
        if len(yearly_aov) > 1:
            fig = px.bar(
                yearly_aov, x="Year", y="Avg Order Value ($)",
                title="Average Order Value — January by Year",
                text_auto=".2s",
                color_discrete_sequence=[PALETTE[0]],
                template=CHART_TEMPLATE,
            )
            fig.update_yaxes(tickprefix="$", tickformat=",.0f")
            _base_layout(fig)
            st.plotly_chart(fig, use_container_width=True)
        else:
            # Distribution of order values in January
            fig = px.histogram(
                jan_orders, x="order_value",
                title="Distribution of Order Values in January",
                labels={"order_value": "Order Value ($)"},
                nbins=30,
                color_discrete_sequence=[PALETTE[0]],
                template=CHART_TEMPLATE,
            )
            fig.add_vline(x=overall_aov, line_dash="dash", line_color="#F59E0B",
                          annotation_text=f"Mean: {fmt_currency(overall_aov)}",
                          annotation_position="top right")
            fig.update_xaxes(tickprefix="$", tickformat=",.0f")
            _base_layout(fig)
            st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        f'<div class="insight-box">📌 <b>January AOV = {fmt_currency(overall_aov)}</b> '
        f'across {fmt_number(n_orders)} orders. AOV = sum of each order\'s total items value ÷ number of distinct orders.</div>',
        unsafe_allow_html=True,
    )


# ── Q3: Highest Brand by Total Order Value in Texas ───────────────────────────

def render_q3_texas_brands(data: dict[str, pd.DataFrame]) -> None:
    """Q3 — Which brand had the highest Total Order Value in Texas?

    Method: filter state == 'Texas' (or 'TX'), sum gross_item_value by brand.

    Args:
        data: Filtered DataFrames.
    """
    df = data["orders"]

    if COL_STATE not in df.columns or COL_BRAND not in df.columns:
        st.warning("Need state and brand columns.")
        return

    texas = df[df[COL_STATE].str.upper().isin(["TEXAS", "TX"])]

    if texas.empty:
        st.info("No Texas data found. Check that state values include 'Texas' or 'TX'.")
        return

    brand_rev = (
        texas.groupby(COL_BRAND)[COL_GROSS_VALUE]
        .sum()
        .reset_index()
        .rename(columns={COL_BRAND: "Brand", COL_GROSS_VALUE: "Total Order Value ($)"})
        .sort_values("Total Order Value ($)", ascending=True)
    )

    winner = brand_rev.iloc[-1]

    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric("🏆 Top Brand in Texas", winner["Brand"])
        st.metric("Total Order Value", fmt_currency(winner["Total Order Value ($)"]))
        st.metric("Texas Brands Ranked", fmt_number(len(brand_rev)))

    with col2:
        # Highlight the winner
        colors = [
            "#0EA5E9" if b == winner["Brand"] else "#BAE6FD"
            for b in brand_rev["Brand"]
        ]
        fig = px.bar(
            brand_rev, x="Total Order Value ($)", y="Brand",
            orientation="h",
            title="Total Order Value by Brand — Texas",
            template=CHART_TEMPLATE,
            text_auto=".2s",
        )
        fig.update_traces(marker_color=colors,
                          hovertemplate="<b>%{y}</b><br>$%{x:,.0f}<extra></extra>")
        fig.update_xaxes(tickprefix="$", tickformat=",.0f")
        _base_layout(fig)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        f'<div class="insight-box">📌 <b>{winner["Brand"]}</b> leads Texas with '
        f'<b>{fmt_currency(winner["Total Order Value ($)"])}</b> in total order value — '
        f'{winner["Total Order Value ($)"] / brand_rev["Total Order Value ($)"].sum():.1%} of all Texas revenue.</div>',
        unsafe_allow_html=True,
    )


# ── Q4: Day of Week & Hour of Day ─────────────────────────────────────────────

_DOW_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def render_q4_day_hour_patterns(data: dict[str, pd.DataFrame]) -> None:
    """Q4 — Which day of week / hour gets the most orders on average?

    Method: count distinct order_ids per (day_of_week, date) →
    average across all weeks. Same logic for hour.

    Args:
        data: Filtered DataFrames.
    """
    df = data["orders"]

    if "day_of_week" not in df.columns:
        st.warning("Need order_datetime to extract day of week / hour.")
        return

    orders = _order_totals(df)

    # ── Day of week: avg orders per day-of-week across all occurrences ────────
    orders["date_only"] = orders[COL_ORDER_DATE].dt.date
    daily_counts = (
        orders.groupby(["day_of_week", "date_only"])[COL_ORDER_ID]
        .count()
        .reset_index()
    )
    avg_by_dow = (
        daily_counts.groupby("day_of_week")[COL_ORDER_ID]
        .mean()
        .reindex(_DOW_ORDER)
        .reset_index()
        .rename(columns={COL_ORDER_ID: "Avg Orders"})
    )
    best_dow = avg_by_dow.loc[avg_by_dow["Avg Orders"].idxmax()]

    col1, col2 = st.columns(2)

    with col1:
        colors_dow = [
            "#0EA5E9" if d == best_dow["day_of_week"] else "#BAE6FD"
            for d in avg_by_dow["day_of_week"]
        ]
        fig = px.bar(
            avg_by_dow, x="day_of_week", y="Avg Orders",
            title="Avg Orders per Day of Week",
            labels={"day_of_week": "Day", "Avg Orders": "Avg Orders"},
            template=CHART_TEMPLATE,
            text_auto=".1f",
        )
        fig.update_traces(marker_color=colors_dow)
        _base_layout(fig)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(
            f'<div class="insight-box">📌 Busiest day: <b>{best_dow["day_of_week"]}</b> '
            f'with <b>{best_dow["Avg Orders"]:.1f}</b> orders on average.</div>',
            unsafe_allow_html=True,
        )

    # ── Hour of day ───────────────────────────────────────────────────────────
    with col2:
        if "hour_of_day" in orders.columns:
            hourly = (
                orders.groupby("hour_of_day")[COL_ORDER_ID]
                .count()
                .reset_index()
                .rename(columns={COL_ORDER_ID: "Order Count", "hour_of_day": "Hour"})
            )
            best_hour = hourly.loc[hourly["Order Count"].idxmax()]

            colors_h = [
                "#0EA5E9" if h == best_hour["Hour"] else "#BAE6FD"
                for h in hourly["Hour"]
            ]
            fig = px.bar(
                hourly, x="Hour", y="Order Count",
                title="Total Orders by Hour of Day",
                labels={"Hour": "Hour (24h)", "Order Count": "Orders"},
                template=CHART_TEMPLATE,
                text_auto=True,
            )
            fig.update_traces(marker_color=colors_h)
            fig.update_xaxes(dtick=1)
            _base_layout(fig)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown(
                f'<div class="insight-box">📌 Busiest hour: <b>{int(best_hour["Hour"]):02d}:00</b> '
                f'with <b>{fmt_number(best_hour["Order Count"])}</b> orders.</div>',
                unsafe_allow_html=True,
            )
        else:
            st.info("order_datetime needed for hourly breakdown.")


# ── Q5: Product Category Analysis + Statistical Test ─────────────────────────

def render_q5_category_analysis(data: dict[str, pd.DataFrame]) -> None:
    """Q5 — Highest avg gross item value by category + significance test.

    Method: group by product_group, compute mean gross_item_value.
    Run one-way ANOVA + post-hoc Tukey HSD between top-2 categories.

    Args:
        data: Filtered DataFrames.
    """
    df = data["orders"]

    if COL_PRODUCT_GROUP not in df.columns or COL_GROSS_VALUE not in df.columns:
        st.warning("Need product_group and gross_item_value columns.")
        return

    valid = df[[COL_PRODUCT_GROUP, COL_GROSS_VALUE]].dropna()

    cat_stats = (
        valid.groupby(COL_PRODUCT_GROUP)[COL_GROSS_VALUE]
        .agg(["mean", "std", "count"])
        .reset_index()
        .rename(columns={
            COL_PRODUCT_GROUP: "Category",
            "mean": "Avg Gross Item Value ($)",
            "std": "Std Dev",
            "count": "N",
        })
        .sort_values("Avg Gross Item Value ($)", ascending=True)
    )

    winner  = cat_stats.iloc[-1]
    second  = cat_stats.iloc[-2] if len(cat_stats) > 1 else None

    col1, col2 = st.columns([2, 1])

    with col1:
        colors_cat = [
            "#0EA5E9" if c == winner["Category"] else "#BAE6FD"
            for c in cat_stats["Category"]
        ]
        fig = px.bar(
            cat_stats, x="Avg Gross Item Value ($)", y="Category",
            orientation="h",
            title="Avg Gross Item Value by Product Category",
            error_x="Std Dev",
            template=CHART_TEMPLATE,
            text_auto=".2s",
            hover_data=["N"],
        )
        fig.update_traces(
            marker_color=colors_cat,
            hovertemplate="<b>%{y}</b><br>Avg: $%{x:,.2f}<br>n=%{customdata[0]}<extra></extra>",
        )
        fig.update_xaxes(tickprefix="$", tickformat=",.2f")
        _base_layout(fig)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.metric("🏆 Top Category", winner["Category"])
        st.metric("Avg Item Value", fmt_currency(winner["Avg Gross Item Value ($)"]))
        st.metric("Sample Size", fmt_number(winner["N"]))

        # ── Statistical significance test (Welch's t-test top-2) ─────────────
        if second is not None:
            st.markdown("**Statistical Test (top 2 categories)**")
            grp1 = valid[valid[COL_PRODUCT_GROUP] == winner["Category"]][COL_GROSS_VALUE]
            grp2 = valid[valid[COL_PRODUCT_GROUP] == second["Category"]][COL_GROSS_VALUE]

            t_stat, p_val = stats.ttest_ind(grp1, grp2, equal_var=False)  # Welch's t-test
            alpha = 0.05
            sig = p_val < alpha

            st.markdown(f"""
| | Value |
|---|---|
| Test | Welch's t-test |
| t-statistic | `{t_stat:.3f}` |
| p-value | `{p_val:.4f}` |
| α | `0.05` |
| Significant? | {'✅ Yes' if sig else '❌ No'} |
""")
            conclusion = (
                f"The difference between **{winner['Category']}** "
                f"(mean={fmt_currency(winner['Avg Gross Item Value ($)'])}) "
                f"and **{second['Category']}** "
                f"(mean={fmt_currency(second['Avg Gross Item Value ($)'])}) "
                f"is **{'statistically significant' if sig else 'NOT statistically significant'}** "
                f"(p={p_val:.4f})."
            )
            st.markdown(
                f'<div class="insight-box">📌 {conclusion}</div>',
                unsafe_allow_html=True,
            )

    # ── Distribution box plot ─────────────────────────────────────────────────
    fig2 = px.box(
        valid.rename(columns={COL_PRODUCT_GROUP: "Category", COL_GROSS_VALUE: "Gross Item Value ($)"}),
        x="Category", y="Gross Item Value ($)",
        title="Distribution of Gross Item Value by Category",
        color="Category",
        color_discrete_sequence=PALETTE,
        template=CHART_TEMPLATE,
        points="outliers",
    )
    fig2.update_yaxes(tickprefix="$", tickformat=",.0f")
    _base_layout(fig2)
    st.plotly_chart(fig2, use_container_width=True)


# ── Bonus Insights ────────────────────────────────────────────────────────────

def render_bonus_insights(data: dict[str, pd.DataFrame]) -> None:
    """Bonus — Additional insights surfaced during analysis.

    Args:
        data: Filtered DataFrames.
    """
    df = data["orders"]
    orders = _order_totals(df)

    col1, col2, col3 = st.columns(3)

    # ── Repeat vs new customers ───────────────────────────────────────────────
    with col1:
        if COL_CUSTOMER_ID in orders.columns:
            order_counts = orders.groupby(COL_CUSTOMER_ID)[COL_ORDER_ID].count()
            repeat = (order_counts > 1).sum()
            new    = (order_counts == 1).sum()
            fig = px.pie(
                names=["Repeat Customers", "One-time Customers"],
                values=[repeat, new],
                title="Customer Retention",
                hole=0.45,
                color_discrete_sequence=[PALETTE[0], "#BAE6FD"],
                template=CHART_TEMPLATE,
            )
            _base_layout(fig, t=48)
            st.plotly_chart(fig, use_container_width=True)

    # ── Revenue by state (top 10) ─────────────────────────────────────────────
    with col2:
        if COL_STATE in df.columns:
            state_rev = (
                df.groupby(COL_STATE)[COL_GROSS_VALUE]
                .sum()
                .reset_index()
                .sort_values(COL_GROSS_VALUE, ascending=False)
                .head(10)
                .rename(columns={COL_STATE: "State", COL_GROSS_VALUE: "Revenue ($)"})
            )
            fig = px.bar(
                state_rev.sort_values("Revenue ($)", ascending=True),
                x="Revenue ($)", y="State",
                orientation="h",
                title="Top 10 States by Revenue",
                color_discrete_sequence=[PALETTE[0]],
                template=CHART_TEMPLATE,
                text_auto=".2s",
            )
            fig.update_xaxes(tickprefix="$", tickformat=",.0f")
            _base_layout(fig)
            st.plotly_chart(fig, use_container_width=True)

    # ── Items per order distribution ──────────────────────────────────────────
    with col3:
        if COL_ITEM_ID in df.columns:
            items_per_order = (
                df.groupby(COL_ORDER_ID)[COL_ITEM_ID]
                .count()
                .reset_index()
                .rename(columns={COL_ITEM_ID: "Items in Order"})
            )
            fig = px.histogram(
                items_per_order, x="Items in Order",
                title="Items per Order Distribution",
                color_discrete_sequence=[PALETTE[0]],
                template=CHART_TEMPLATE,
                nbins=20,
            )
            avg_items = items_per_order["Items in Order"].mean()
            fig.add_vline(x=avg_items, line_dash="dash", line_color="#F59E0B",
                          annotation_text=f"Mean: {avg_items:.1f}",
                          annotation_position="top right")
            _base_layout(fig)
            st.plotly_chart(fig, use_container_width=True)