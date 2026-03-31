import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from utils.charts import base_layout, fmt_currency, fmt_number, PALETTE


def render(full_df: pd.DataFrame, filtered_df: pd.DataFrame) -> None:
    st.markdown("## 🎁 Promo Insight — Free Gift Analysis")

    st.markdown("""
    <div class="insight-box">
        <b>Finding:</b> Brand 2 and Brand 3 bundle a free <b>Category 8</b> item with orders
        as an ongoing promotion. Evidence: 92 zero-value rows concentrated in Brand 2/3 × Category 8,
        spread across the full date range (~1 per unique customer), with no single-day spike.
        <br><br>
        <b>Key question:</b> Did customers who received the free gift spend more on paid items?
        If yes, the promo is driving upsell — it earns its cost.
    </div>
    """, unsafe_allow_html=True)

    # ── Isolate promo vs non-promo orders ────────────────────────────────────
    revenue_df = full_df[full_df["gross_item_value"] > 0].copy()

    promo_order_ids = full_df[full_df["is_promo_zero"]]["order_id"].unique()

    orders_with_promo    = revenue_df[revenue_df["order_id"].isin(promo_order_ids)]
    orders_without_promo = revenue_df[~revenue_df["order_id"].isin(promo_order_ids)]

    aov_with    = orders_with_promo.groupby("order_id")["gross_item_value"].sum().mean()
    aov_without = orders_without_promo.groupby("order_id")["gross_item_value"].sum().mean()
    n_promo     = len(promo_order_ids)
    n_no_promo  = orders_without_promo["order_id"].nunique()
    uplift_pct  = (aov_with - aov_without) / aov_without * 100 if aov_without else 0

    # ── KPIs ──────────────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Promo Orders",          fmt_number(n_promo))
    c2.metric("Non-promo Orders",      fmt_number(n_no_promo))
    c3.metric("AOV — With Promo",      fmt_currency(aov_with))
    c4.metric("AOV — Without Promo",   fmt_currency(aov_without))

    st.markdown("---")

    col_a, col_b = st.columns(2)

    # ── AOV comparison bar ────────────────────────────────────────────────────
    with col_a:
        st.markdown('<p class="section-title">AOV: Promo vs No Promo</p>', unsafe_allow_html=True)
        fig = go.Figure(go.Bar(
            x=["With Free Gift", "Without Free Gift"],
            y=[aov_with, aov_without],
            marker_color=[PALETTE[0], PALETTE[1]],
            opacity=0.8,
            text=[fmt_currency(aov_with), fmt_currency(aov_without)],
            textposition="outside",
        ))
        fig.update_layout(title="Average Order Value by Promo Status")
        fig.update_yaxes(tickprefix="$", tickformat=",.0f")
        base_layout(fig, height=280)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # ── Spend distribution overlay ────────────────────────────────────────────
    with col_b:
        st.markdown('<p class="section-title">Spend Distribution Comparison</p>', unsafe_allow_html=True)

        spend_with    = orders_with_promo.groupby("order_id")["gross_item_value"].sum()
        spend_without = orders_without_promo.groupby("order_id")["gross_item_value"].sum()

        p99 = max(spend_with.quantile(0.99), spend_without.quantile(0.99))

        fig2 = go.Figure()
        fig2.add_trace(go.Histogram(
            x=spend_without[spend_without <= p99],
            nbinsx=30,
            name="Without Promo",
            marker_color=PALETTE[1],
            opacity=0.6,
        ))
        fig2.add_trace(go.Histogram(
            x=spend_with[spend_with <= p99],
            nbinsx=30,
            name="With Promo",
            marker_color=PALETTE[0],
            opacity=0.6,
        ))
        fig2.update_layout(
            title="Order Spend Distribution (1st–99th pct)",
            barmode="overlay",
        )
        fig2.update_xaxes(tickprefix="$", tickformat=",.0f", title="Order Value ($)")
        fig2.update_yaxes(title="Count")
        base_layout(fig2, height=280)
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

    st.markdown("---")

    # ── Customer behaviour after promo ────────────────────────────────────────
    st.markdown('<p class="section-title">Customer Behaviour After Receiving Free Gift</p>',
                unsafe_allow_html=True)

    st.markdown("""
    <div class="insight-box">
        Did customers who received the free gift come back and buy again?
        We identify customers who had a promo order, then check whether they placed
        a <b>subsequent paid order</b> after that date.
    </div>
    """, unsafe_allow_html=True)

    # Customers who got the promo
    promo_customers = full_df[full_df["is_promo_zero"]][["customer_id", "order_date"]].copy()
    promo_customers = promo_customers.rename(columns={"order_date": "promo_date"})
    promo_customers = promo_customers.groupby("customer_id")["promo_date"].min().reset_index()

    # All paid orders
    paid_orders = revenue_df[["customer_id", "order_id", "order_date"]].drop_duplicates()

    # Join and find orders AFTER the promo date
    behaviour = paid_orders.merge(promo_customers, on="customer_id", how="inner")
    behaviour["days_since_promo"] = (behaviour["order_date"] - behaviour["promo_date"]).dt.days

    returned_df   = behaviour[behaviour["days_since_promo"] > 0]
    n_promo_custs = promo_customers["customer_id"].nunique()
    n_returned    = returned_df["customer_id"].nunique()
    return_rate   = n_returned / n_promo_custs * 100 if n_promo_custs else 0

    c1, c2, c3 = st.columns(3)
    c1.metric("Customers Received Promo",  fmt_number(n_promo_custs))
    c2.metric("Returned to Buy Again",     fmt_number(n_returned))
    c3.metric("Post-Promo Return Rate",    f"{return_rate:.1f}%")

    col_c, col_d = st.columns(2)

    # ── Days to return distribution ───────────────────────────────────────────
    with col_c:
        st.markdown('<p class="section-title">Days from Promo to Next Purchase</p>',
                    unsafe_allow_html=True)

        first_return = (
            returned_df.groupby("customer_id")["days_since_promo"]
            .min()
            .reset_index()
        )
        fig3 = go.Figure(go.Histogram(
            x=first_return["days_since_promo"],
            nbinsx=25,
            marker_color=PALETTE[2],
            opacity=0.8,
        ))
        avg_days = first_return["days_since_promo"].mean()
        fig3.add_vline(x=avg_days, line_dash="dash", line_color=PALETTE[3],
                       annotation_text=f"Avg {avg_days:.0f} days",
                       annotation_position="top right")
        fig3.update_layout(title="How Quickly Did Customers Return?")
        fig3.update_xaxes(title="Days After Promo")
        fig3.update_yaxes(title="Customers")
        base_layout(fig3, height=280)
        st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})

    # ── Revenue from returning vs non-returning promo customers ──────────────
    with col_d:
        st.markdown('<p class="section-title">Revenue: Returning vs Non-returning Promo Customers</p>',
                    unsafe_allow_html=True)

        returning_ids     = returned_df["customer_id"].unique()
        non_returning_ids = promo_customers[
            ~promo_customers["customer_id"].isin(returning_ids)
        ]["customer_id"].unique()

        rev_returning     = revenue_df[revenue_df["customer_id"].isin(returning_ids)]["gross_item_value"].sum()
        rev_non_returning = revenue_df[revenue_df["customer_id"].isin(non_returning_ids)]["gross_item_value"].sum()

        fig4 = go.Figure(go.Bar(
            x=["Returned After Promo", "Did Not Return"],
            y=[rev_returning, rev_non_returning],
            marker_color=[PALETTE[0], PALETTE[5]],
            opacity=0.8,
            text=[fmt_currency(rev_returning), fmt_currency(rev_non_returning)],
            textposition="outside",
        ))
        fig4.update_layout(title="Total Revenue by Post-Promo Behaviour")
        fig4.update_yaxes(tickprefix="$", tickformat=",.0f")
        base_layout(fig4, height=280)
        st.plotly_chart(fig4, use_container_width=True, config={"displayModeBar": False})

    # ── Summary verdict ───────────────────────────────────────────────────────
    st.markdown("---")
    if uplift_pct > 5:
        verdict = f"✅ Promo appears effective — orders with a free gift show <b>{uplift_pct:.1f}% higher AOV</b>. The promotion is likely driving upsell or attracting higher-intent buyers."
    elif uplift_pct > 0:
        verdict = f"⚠️ Marginal uplift — orders with a free gift show only <b>{uplift_pct:.1f}% higher AOV</b>. Monitor over a longer period before drawing conclusions."
    else:
        verdict = f"❌ No positive uplift detected — promo orders have <b>{abs(uplift_pct):.1f}% lower AOV</b>. The free gift may be attracting low-intent buyers or cannibalising full-price sales."

    st.markdown(f"""
    <div class="insight-box">
        <b>Promo Effectiveness Verdict</b><br>
        {verdict}<br><br>
        <b>Return behaviour:</b> {return_rate:.1f}% of customers who received a free gift
        placed a subsequent paid order, with an average of {avg_days:.0f} days before returning.
    </div>
    """, unsafe_allow_html=True)