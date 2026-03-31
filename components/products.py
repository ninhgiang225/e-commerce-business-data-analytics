"""Product & Brand — Q3 Texas, Q5 Category Item Value."""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from scipy import stats
from utils.charts import base_layout, fmt_currency, fmt_number, PALETTE, TEAL, AMBER, PURPLE, BLUE, LABEL_COLOR


def render(df: pd.DataFrame, revenue_df: pd.DataFrame) -> None:
    st.markdown("## Product & Brand Analytics")

    # ── Q3: Top brand in Texas ────────────────────────────────────────────────
    st.markdown('<p class="section-header">Q3 — Highest Total Order Value in Texas</p>',
                unsafe_allow_html=True)

    texas_df = revenue_df[revenue_df["state"].str.upper().isin(["TX", "TEXAS"])].copy()

    if texas_df.empty:
        st.warning("No Texas orders found in the current filter selection.")
    else:
        brand_totals = (
            texas_df.groupby("brand")["gross_item_value"]
            .sum().sort_values(ascending=False).reset_index()
        )
        winner       = brand_totals.iloc[0]
        total_texas  = texas_df["gross_item_value"].sum()
        winner_share = winner["gross_item_value"] / total_texas * 100

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Top Brand in Texas",       winner["brand"])
        c2.metric("Top Brand Revenue (TX)",   fmt_currency(winner["gross_item_value"]))
        c3.metric("Total Texas Revenue",      fmt_currency(total_texas))
        c4.metric("Top Brand Share",          f"{winner_share:.1f}%")

        col_a, col_b = st.columns([3, 2])

        with col_a:
            colors = [TEAL if b == winner["brand"] else "#A8D5D1"
                      for b in brand_totals["brand"]]
            fig = go.Figure(go.Bar(
                x=brand_totals["brand"],
                y=brand_totals["gross_item_value"],
                marker_color=colors,
                opacity=0.90,
                text=[fmt_currency(v) for v in brand_totals["gross_item_value"]],
                textposition="outside",
                textfont=dict(size=12, color="#1A202C"),
                showlegend=False,
                hovertemplate="%{x}<br><b>$%{y:,.0f}</b><extra></extra>",
            ))
            fig.update_layout(title="Total Order Value by Brand — Texas")
            fig.update_yaxes(tickprefix="$", tickformat=",.0f", title="Total Order Value ($)")
            fig.update_xaxes(title="Brand")
            base_layout(fig, height=320)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        with col_b:
            fig2 = go.Figure(go.Pie(
                labels=brand_totals["brand"],
                values=brand_totals["gross_item_value"],
                hole=0.48,
                marker_colors=PALETTE[:len(brand_totals)],
                textinfo="label+percent",
                textfont=dict(size=12, color="#1A202C"),
                pull=[0.06 if b == winner["brand"] else 0
                      for b in brand_totals["brand"]],
            ))
            fig2.update_layout(
                title="Revenue Share in Texas",
                showlegend=False,
                annotations=[dict(
                    text=f"<b>{winner['brand']}</b><br>{winner_share:.0f}%",
                    x=0.5, y=0.5, font_size=14, showarrow=False,
                    font=dict(color="#1A202C"),
                )],
            )
            base_layout(fig2, height=320)
            st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

        # Texas vs national share
        national_share = (
            revenue_df.groupby("brand")["gross_item_value"].sum()
            .div(revenue_df["gross_item_value"].sum()) * 100
        ).rename("National %")
        texas_share = (
            brand_totals.set_index("brand")["gross_item_value"]
            .div(total_texas) * 100
        ).rename("Texas %")
        compare = pd.concat([national_share, texas_share], axis=1).fillna(0).reset_index()

        fig3 = go.Figure()
        fig3.add_bar(x=compare["brand"], y=compare["National %"],
                     name="National", marker_color=TEAL, opacity=0.85)
        fig3.add_bar(x=compare["brand"], y=compare["Texas %"],
                     name="Texas",    marker_color=AMBER, opacity=0.85)
        fig3.update_layout(
            title="Brand Revenue Share — Texas vs National (%)",
            barmode="group",
        )
        fig3.update_yaxes(ticksuffix="%", title="Share of Revenue (%)")
        fig3.update_xaxes(title="Brand")
        base_layout(fig3, height=300)
        st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})

        st.markdown(f"""
        <div class="insight-box">
            <b>{winner["brand"]}</b> leads Texas with
            <b>{fmt_currency(winner["gross_item_value"])}</b>, representing
            <b>{winner_share:.1f}%</b> of all Texas revenue.
            Compare Texas share vs national share to assess regional
            over- or under-performance by brand.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Q5: Avg Gross Item Value by Category ──────────────────────────────────
    st.markdown('<p class="section-header">Q5 — Avg Gross Item Value by Category (zero-value promos excluded)</p>',
                unsafe_allow_html=True)

    avg_item = revenue_df["gross_item_value"].mean()
    med_item = revenue_df["gross_item_value"].median()
    n_promos = df["is_promo_zero"].sum()

    c1, c2, c3 = st.columns(3)
    c1.metric("Avg Gross Item Value",    fmt_currency(avg_item))
    c2.metric("Median Gross Item Value", fmt_currency(med_item))
    c3.metric("Promo Items Excluded",    fmt_number(n_promos))

    st.markdown("""
    <div class="warn-box">
        Brand 2 and Brand 3 bundle a free Category 8 item per order as an ongoing promotion.
        These zero-value rows are excluded to avoid deflating the category average.
    </div>
    """, unsafe_allow_html=True)

    cat_stats = (
        revenue_df.groupby("product_group")["gross_item_value"]
        .agg(mean_value="mean", median_value="median",
             n_items="count", std_value="std")
        .sort_values("mean_value", ascending=False)
        .reset_index()
    )
    winner_cat = cat_stats.iloc[0]
    runner_up  = cat_stats.iloc[1] if len(cat_stats) > 1 else None

    col_c, col_d = st.columns([3, 2])

    with col_c:
        fig4 = go.Figure()
        fig4.add_bar(
            x=cat_stats["product_group"], y=cat_stats["mean_value"],
            name="Mean", marker_color=TEAL, opacity=0.85,
            error_y=dict(
                type="data",
                array=(cat_stats["std_value"] / np.sqrt(cat_stats["n_items"])).tolist(),
                visible=True, color="#718096", thickness=1.5, width=4,
            ),
            hovertemplate="%{x}<br>Mean: <b>$%{y:,.2f}</b><extra></extra>",
        )
        fig4.add_bar(
            x=cat_stats["product_group"], y=cat_stats["median_value"],
            name="Median", marker_color=AMBER, opacity=0.85,
            hovertemplate="%{x}<br>Median: <b>$%{y:,.2f}</b><extra></extra>",
        )
        fig4.update_layout(
            title="Avg Gross Item Value by Category (error bars = 95% CI of mean)",
            barmode="group",
        )
        fig4.update_yaxes(tickprefix="$", tickformat=",.2f", title="Gross Item Value ($)")
        fig4.update_xaxes(title="Product Category", tickangle=-30)
        base_layout(fig4, height=340)
        st.plotly_chart(fig4, use_container_width=True, config={"displayModeBar": False})

    with col_d:
        if runner_up is not None:
            top_vals    = revenue_df[revenue_df["product_group"] == winner_cat["product_group"]]["gross_item_value"]
            second_vals = revenue_df[revenue_df["product_group"] == runner_up["product_group"]]["gross_item_value"]
            _, p_value  = stats.ttest_ind(top_vals, second_vals, equal_var=False)
            sig         = p_value < 0.05

            p99        = revenue_df["gross_item_value"].quantile(0.99)
            compare_df = revenue_df[
                revenue_df["product_group"].isin(
                    [winner_cat["product_group"], runner_up["product_group"]]
                ) & (revenue_df["gross_item_value"] <= p99)
            ]
            fig5 = go.Figure()
            for i, cat in enumerate([winner_cat["product_group"], runner_up["product_group"]]):
                vals = compare_df[compare_df["product_group"] == cat]["gross_item_value"]
                fig5.add_trace(go.Box(
                    y=vals, name=cat,
                    marker_color=PALETTE[i], boxmean="sd", line_width=1.5,
                ))
            fig5.update_layout(title="Top 2 Categories — Value Distribution (up to 99th pct)")
            fig5.update_yaxes(tickprefix="$", tickformat=",.2f", title="Item Value ($)")
            base_layout(fig5, height=340)
            st.plotly_chart(fig5, use_container_width=True, config={"displayModeBar": False})

            verdict_bg     = "#EBF8FF" if sig else "#FFF5F5"
            verdict_border = TEAL if sig else "#E8607A"
            verdict_text   = (
                f"Statistically significant (p = {p_value:.4f}, below 0.05). "
                f"<b>{winner_cat['product_group']}</b> genuinely outperforms "
                f"<b>{runner_up['product_group']}</b>."
            ) if sig else (
                f"Not statistically significant (p = {p_value:.4f}, above 0.05). "
                f"The gap between <b>{winner_cat['product_group']}</b> and "
                f"<b>{runner_up['product_group']}</b> may be due to random variation."
            )
            st.markdown(f"""
            <div style="background:{verdict_bg}; border-left:4px solid {verdict_border};
                        padding:12px 16px; border-radius:0 8px 8px 0;
                        font-size:0.9rem; color:#1A202C; line-height:1.7; margin-top:8px;">
                <b>Welch's t-test:</b> {winner_cat['product_group']} vs {runner_up['product_group']}<br><br>
                {verdict_text}
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Brand revenue breakdown ───────────────────────────────────────────────
    st.markdown('<p class="section-header">Brand Revenue Breakdown</p>', unsafe_allow_html=True)

    col_e, col_f = st.columns(2)

    with col_e:
        brand_rev = (
            revenue_df.groupby("brand")["gross_item_value"]
            .sum().sort_values(ascending=True).reset_index()
        )
        fig6 = go.Figure(go.Bar(
            x=brand_rev["gross_item_value"], y=brand_rev["brand"],
            orientation="h", marker_color=PURPLE, opacity=0.85,
            showlegend=False,
            hovertemplate="%{y}<br><b>$%{x:,.0f}</b><extra></extra>",
        ))
        fig6.update_layout(title="Total Revenue by Brand")
        fig6.update_xaxes(tickprefix="$", tickformat=",.0f", title="Revenue ($)")
        fig6.update_yaxes(title="")
        base_layout(fig6, height=300)
        st.plotly_chart(fig6, use_container_width=True, config={"displayModeBar": False})

    with col_f:
        brand_share = (
            revenue_df.groupby("brand")["gross_item_value"]
            .sum().reset_index().sort_values("gross_item_value", ascending=False)
        )
        fig7 = go.Figure(go.Pie(
            labels=brand_share["brand"],
            values=brand_share["gross_item_value"],
            hole=0.45,
            marker_colors=PALETTE[:len(brand_share)],
            textinfo="label+percent",
            textfont=dict(size=12, color="#1A202C"),
        ))
        fig7.update_layout(title="Revenue Share by Brand", showlegend=False)
        base_layout(fig7, height=300)
        st.plotly_chart(fig7, use_container_width=True, config={"displayModeBar": False})