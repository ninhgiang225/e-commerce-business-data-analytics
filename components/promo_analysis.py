import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from utils.charts import base_layout, fmt_currency, fmt_number, PALETTE


def render(full_df: pd.DataFrame, filtered_df: pd.DataFrame) -> None:
    st.markdown("## Promo Insight — Free Gift Analysis")

    # ── Shared setup ──────────────────────────────────────────────────────────
    revenue_df      = full_df[full_df["gross_item_value"] > 0].copy()
    promo_order_ids = full_df[full_df["is_promo_zero"]]["order_id"].unique()

    promo_customers = (
        full_df[full_df["is_promo_zero"]][["customer_id", "order_date"]]
        .rename(columns={"order_date": "promo_date"})
        .groupby("customer_id")["promo_date"]
        .min()
        .reset_index()
    )
    promo_customer_ids = set(promo_customers["customer_id"].unique())
    n_promo_custs      = len(promo_customer_ids)

    # Customers who returned with a paid non-promo order after their promo date
    paid_orders = revenue_df[["customer_id", "order_id", "order_date"]].drop_duplicates()
    behaviour   = paid_orders.merge(promo_customers, on="customer_id", how="inner")
    behaviour["days_since_promo"] = (behaviour["order_date"] - behaviour["promo_date"]).dt.days
    returned_df = behaviour[behaviour["days_since_promo"] > 0]
    n_returned  = returned_df["customer_id"].nunique()

    # Overlap: non-promo paid orders by promo customers placed after promo date
    overlap_orders = (
        revenue_df[
            revenue_df["customer_id"].isin(promo_customer_ids) &
            ~revenue_df["order_id"].isin(promo_order_ids)
        ]
        .merge(promo_customers, on="customer_id", how="left")
    )
    overlap_orders["days_after_promo"] = (
        overlap_orders["order_date"] - overlap_orders["promo_date"]
    ).dt.days
    overlap_orders = overlap_orders[overlap_orders["days_after_promo"] > 0]

    n_overlap_custs = overlap_orders["customer_id"].nunique()
    overlap_rate    = n_overlap_custs / n_promo_custs * 100 if n_promo_custs else 0
    overlap_rev     = overlap_orders["gross_item_value"].sum()

    # CLV
    promo_clv         = revenue_df[revenue_df["customer_id"].isin(promo_customer_ids)].groupby("customer_id")["gross_item_value"].sum()
    non_promo_clv     = revenue_df[~revenue_df["customer_id"].isin(promo_customer_ids)].groupby("customer_id")["gross_item_value"].sum()
    avg_promo_clv     = promo_clv.mean() if len(promo_clv) else 0
    avg_non_promo_clv = non_promo_clv.mean() if len(non_promo_clv) else 0
    clv_lift_pct      = (avg_promo_clv - avg_non_promo_clv) / avg_non_promo_clv * 100 if avg_non_promo_clv else 0

    # Basket data (paid items only, zero-value gift excluded)
    promo_paid     = revenue_df[revenue_df["order_id"].isin(promo_order_ids)].copy()
    non_promo_paid = revenue_df[~revenue_df["order_id"].isin(promo_order_ids)].copy()
    avg_item_promo     = promo_paid["gross_item_value"].mean()
    avg_item_non_promo = non_promo_paid["gross_item_value"].mean()
    item_lift_pct      = (avg_item_promo - avg_item_non_promo) / avg_item_non_promo * 100 if avg_item_non_promo else 0

    # Time-to-next-purchase
    all_orders = (
        revenue_df[["customer_id", "order_id", "order_date"]]
        .drop_duplicates()
        .sort_values(["customer_id", "order_date"])
    )
    all_orders["prev_order_date"] = all_orders.groupby("customer_id")["order_date"].shift(1)
    all_orders["interval_days"]   = (all_orders["order_date"] - all_orders["prev_order_date"]).dt.days
    intervals = all_orders.dropna(subset=["interval_days"])
    intervals["is_promo_customer"] = intervals["customer_id"].isin(promo_customer_ids)
    promo_intervals     = intervals[intervals["is_promo_customer"]]["interval_days"]
    non_promo_intervals = intervals[~intervals["is_promo_customer"]]["interval_days"]
    avg_promo_int     = promo_intervals.mean() if len(promo_intervals) else 0
    avg_non_promo_int = non_promo_intervals.mean() if len(non_promo_intervals) else 0
    interval_diff     = avg_promo_int - avg_non_promo_int

    # ── 4 KPI cards ───────────────────────────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Promo Customers",         fmt_number(n_promo_custs))
    k2.metric("Made Non-promo Purchase", fmt_number(n_overlap_custs))
    k3.metric("Return Rate",             f"{overlap_rate:.1f}%")
    k4.metric("Revenue from Returning",  fmt_currency(overlap_rev))

    st.markdown("---")

    # ── Row 1: CLV histogram  |  Return frequency bar ─────────────────────────
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown('<p class="section-title">Lifetime Spend: Promo vs Non-promo Customers</p>',
                    unsafe_allow_html=True)

        p99_clv = max(
            promo_clv.quantile(0.99) if len(promo_clv) else 0,
            non_promo_clv.quantile(0.99) if len(non_promo_clv) else 0,
        )
        fig_clv = go.Figure()
        fig_clv.add_trace(go.Histogram(
            x=non_promo_clv[non_promo_clv <= p99_clv],
            nbinsx=30, name="Non-promo customers",
            marker_color=PALETTE[1], opacity=0.6,
        ))
        fig_clv.add_trace(go.Histogram(
            x=promo_clv[promo_clv <= p99_clv],
            nbinsx=30, name="Promo customers",
            marker_color=PALETTE[0], opacity=0.75,
        ))
        fig_clv.add_vline(x=avg_non_promo_clv, line_dash="dash", line_color=PALETTE[1],
                          annotation_text=f"Non-promo avg {fmt_currency(avg_non_promo_clv)}",
                          annotation_position="top left")
        fig_clv.add_vline(x=avg_promo_clv, line_dash="dash", line_color=PALETTE[0],
                          annotation_text=f"Promo avg {fmt_currency(avg_promo_clv)}",
                          annotation_position="top right")
        fig_clv.update_layout(title="Customer Lifetime Spend Distribution", barmode="overlay")
        fig_clv.update_xaxes(tickprefix="$", tickformat=",.0f", title="Total Lifetime Spend ($)")
        fig_clv.update_yaxes(title="Customers")
        base_layout(fig_clv, height=320)
        st.plotly_chart(fig_clv, use_container_width=True, config={"displayModeBar": False})
        st.caption(
            f"Promo customers avg {fmt_currency(avg_promo_clv)} vs "
            f"{fmt_currency(avg_non_promo_clv)} non-promo ({clv_lift_pct:+.1f}% difference)."
        )

    with col_b:
        st.markdown('<p class="section-title">How Many Times Did Customers Return?</p>',
                    unsafe_allow_html=True)

        if n_overlap_custs > 0:
            orders_after = (
                overlap_orders.groupby("customer_id")["order_id"]
                .nunique()
                .value_counts()
                .reset_index()
                .rename(columns={"order_id": "num_orders", "count": "customers"})
                .sort_values("num_orders")
            )
            avg_overlap_orders = overlap_orders.groupby("customer_id")["order_id"].nunique().mean()

            fig_freq = go.Figure(go.Bar(
                x=orders_after["num_orders"].astype(str) + " order(s)",
                y=orders_after["customers"],
                marker_color=PALETTE[2], opacity=0.85,
                text=orders_after["customers"], textposition="outside",
            ))
            fig_freq.update_layout(
                title=f"Non-promo Orders Placed by {n_overlap_custs} Returning Customers",
            )
            fig_freq.update_xaxes(title="Non-promo Orders After Receiving Gift")
            fig_freq.update_yaxes(title="Customers")
            base_layout(fig_freq, height=320)
            st.plotly_chart(fig_freq, use_container_width=True, config={"displayModeBar": False})
            st.caption(f"Avg {avg_overlap_orders:.1f} non-promo orders per overlap customer.")
        else:
            st.info("No promo customers placed a subsequent non-promo order in this date range.")

    st.markdown("---")

    # ── Row 2: Category revenue share  |  Days to return ─────────────────────
    col_c, col_d = st.columns(2)

    with col_c:
        st.markdown('<p class="section-title">Category Revenue Share — Promo vs Non-promo</p>',
                    unsafe_allow_html=True)

        cat_col = "product_group" if "product_group" in revenue_df.columns else "brand"

        promo_cat = (
            promo_paid.groupby(cat_col)["gross_item_value"].sum()
            .rename("promo_rev").reset_index().rename(columns={cat_col: "category"})
        )
        non_promo_cat = (
            non_promo_paid.groupby(cat_col)["gross_item_value"].sum()
            .rename("non_promo_rev").reset_index().rename(columns={cat_col: "category"})
        )
        cat_mix = promo_cat.merge(non_promo_cat, on="category", how="outer").fillna(0)
        cat_mix["promo_share"]     = cat_mix["promo_rev"] / cat_mix["promo_rev"].sum() * 100
        cat_mix["non_promo_share"] = cat_mix["non_promo_rev"] / cat_mix["non_promo_rev"].sum() * 100
        cat_mix["total"]           = cat_mix["promo_rev"] + cat_mix["non_promo_rev"]
        cat_mix = cat_mix.nlargest(10, "total").sort_values("promo_share")

        fig_cat = go.Figure()
        fig_cat.add_trace(go.Bar(
            y=cat_mix["category"].astype(str), x=cat_mix["non_promo_share"],
            name="Non-promo", orientation="h", marker_color=PALETTE[1], opacity=0.75,
        ))
        fig_cat.add_trace(go.Bar(
            y=cat_mix["category"].astype(str), x=cat_mix["promo_share"],
            name="Promo (excl. gift)", orientation="h", marker_color=PALETTE[0], opacity=0.75,
        ))
        fig_cat.update_layout(
            title="Revenue Share by Category (top 10, paid items only)",
            barmode="group",
        )
        fig_cat.update_xaxes(title="Share of Revenue (%)", ticksuffix="%")
        base_layout(fig_cat, height=320)
        st.plotly_chart(fig_cat, use_container_width=True, config={"displayModeBar": False})

    with col_d:
        st.markdown('<p class="section-title">How Quickly Did Customers Return?</p>',
                    unsafe_allow_html=True)

        if n_returned > 0:
            first_return = (
                returned_df.groupby("customer_id")["days_since_promo"]
                .min().reset_index()
            )
            avg_days = first_return["days_since_promo"].mean()

            fig_ret = go.Figure(go.Histogram(
                x=first_return["days_since_promo"],
                nbinsx=25,
                marker_color=PALETTE[2],
                opacity=0.8,
            ))
            fig_ret.add_vline(x=avg_days, line_dash="dash", line_color=PALETTE[3],
                              annotation_text=f"Avg {avg_days:.0f} days",
                              annotation_position="top right")
            fig_ret.update_layout(title="Days from Promo to Next Purchase")
            fig_ret.update_xaxes(title="Days After Promo")
            fig_ret.update_yaxes(title="Customers")
            base_layout(fig_ret, height=320)
            st.plotly_chart(fig_ret, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("No promo customers placed a return order in this date range.")

    # ── Verdict ───────────────────────────────────────────────────────────────
    st.markdown("---")

    signals = []
    if overlap_rate >= 20:
        signals.append(f"<b>{overlap_rate:.0f}%</b> of promo customers converted to repeat non-promo buyers — strong CLV signal.")
    elif overlap_rate > 0:
        signals.append(f" Only <b>{overlap_rate:.0f}%</b> of promo customers converted to non-promo buyers.")
    else:
        signals.append(" No promo customers made a subsequent non-promo purchase in this period.")


    any_positive = any("✅" in s for s in signals)
    recommendation = (
        "Overall signals are positive. The free gift appears to be earning its cost by converting "
        "recipients into repeat buyers with higher lifetime value."
        if any_positive else
        "Consider A/B testing the promo against a discount-equivalent offer to isolate the "
        "free-gift effect from price sensitivity."
    )

    st.markdown(f"""
    <div class="insight-box">
        {"<br>".join(f"&nbsp;&nbsp;{s}" for s in signals)}<br><br>
        {recommendation}
    </div>
    """, unsafe_allow_html=True)