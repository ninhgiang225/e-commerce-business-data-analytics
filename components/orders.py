"""Order Analytics — Total Order Value by Day, AOV January, Q4 Day/Hour."""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from utils.charts import base_layout, fmt_currency, fmt_number, TEAL, AMBER, PURPLE, BLUE, PALETTE, LABEL_COLOR

DAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def render(df: pd.DataFrame, revenue_df: pd.DataFrame) -> None:
    st.markdown("## Order Analytics")

    # ── Total Order Value by Day ───────────────────────────────────────────────
    st.markdown('<p class="section-header">Q1 — Total Order Value by Day</p>', unsafe_allow_html=True)

    daily = (
        revenue_df.groupby("order_date")["gross_item_value"]
        .sum().reset_index().sort_values("order_date")
    )
    daily["rolling_7"] = daily["gross_item_value"].rolling(7, min_periods=1).mean()
    peak_row = daily.loc[daily["gross_item_value"].idxmax()]

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Revenue",     fmt_currency(daily["gross_item_value"].sum()))
    c2.metric("Avg Daily Revenue", fmt_currency(daily["gross_item_value"].mean()))
    c3.metric("Peak Day",
              f"{peak_row['order_date'].strftime('%b %d')}  "
              f"{fmt_currency(peak_row['gross_item_value'])}")

    fig = go.Figure()
    fig.add_bar(
        x=daily["order_date"], y=daily["gross_item_value"],
        marker_color=TEAL, opacity=0.75, name="Daily Revenue",
        hovertemplate="%{x|%b %d}<br><b>$%{y:,.0f}</b><extra></extra>",
    )
    fig.add_scatter(
        x=daily["order_date"], y=daily["rolling_7"],
        mode="lines", line=dict(color=AMBER, width=2.5, dash="dot"),
        name="7-day rolling avg",
        hovertemplate="%{x|%b %d}<br>7-day avg: <b>$%{y:,.0f}</b><extra></extra>",
    )
    fig.add_annotation(
        x=peak_row["order_date"], y=peak_row["gross_item_value"],
        text=f"Peak  {fmt_currency(peak_row['gross_item_value'])}",
        showarrow=True, arrowhead=2, arrowcolor=AMBER, arrowwidth=1.5,
        ax=0, ay=-44, font=dict(size=12, color="#1A202C"),
        bgcolor="white", bordercolor=AMBER, borderwidth=1, borderpad=4,
    )
    fig.update_layout(title="Total Order Value by Day")
    fig.update_yaxes(tickprefix="$", tickformat=",.0f", title="Order Value ($)")
    fig.update_xaxes(title="Date")
    base_layout(fig, height=360)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.markdown("---")

    # ── AOV in January ────────────────────────────────────────────────────────
    st.markdown('<p class="section-header">Q2 — Average Order Value in January</p>',
                unsafe_allow_html=True)

    jan_df     = revenue_df[revenue_df["order_date"].dt.month == 1]
    jan_orders = jan_df.groupby("order_id")["gross_item_value"].sum().reset_index()
    jan_orders.columns = ["order_id", "order_value"]
    jan_aov    = jan_orders["order_value"].mean()
    jan_median = jan_orders["order_value"].median()
    n_jan      = len(jan_orders)

    c1, c2, c3 = st.columns(3)
    c1.metric("January AOV (mean)",   fmt_currency(jan_aov))
    c2.metric("January AOV (median)", fmt_currency(jan_median))
    c3.metric("January Orders",       fmt_number(n_jan))

    q01     = jan_orders["order_value"].quantile(0.01)
    q99     = jan_orders["order_value"].quantile(0.99)
    plot_df = jan_orders[jan_orders["order_value"].between(q01, q99)]
    n_excl  = len(jan_orders) - len(plot_df)

    col_a, col_b = st.columns([3, 2])

    with col_a:
        fig2 = go.Figure(go.Histogram(
            x=plot_df["order_value"], nbinsx=30,
            marker_color=TEAL, opacity=0.80, name="Order Value",
            hovertemplate="$%{x:,.0f}<br>Count: <b>%{y}</b><extra></extra>",
        ))
        fig2.add_vline(x=jan_aov, line_dash="dash", line_color=AMBER, line_width=2,
                       annotation_text=f"Mean  {fmt_currency(jan_aov)}",
                       annotation_position="top right",
                       annotation_font=dict(color="#1A202C", size=12))
        fig2.add_vline(x=jan_median, line_dash="dot", line_color=PURPLE, line_width=2,
                       annotation_text=f"Median  {fmt_currency(jan_median)}",
                       annotation_position="top left",
                       annotation_font=dict(color="#1A202C", size=12))
        fig2.update_layout(title="Distribution of January Order Values (1st–99th Percentile)")
        fig2.update_xaxes(tickprefix="$", tickformat=",.0f", title="Order Value ($)")
        fig2.update_yaxes(title="Number of Orders")
        base_layout(fig2, height=300)
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
        if n_excl:
            st.caption(f"{n_excl} orders outside 1st–99th percentile hidden. "
                       f"Metrics computed on all orders.")

    with col_b:
        q_labels = ["Q1 (0–25%)", "Q2 (25–50%)", "Q3 (50–75%)", "Q4 (75–100%)"]
        q_vals   = [jan_orders["order_value"].quantile(q) for q in [0.25, 0.50, 0.75, 1.0]]
        fig3 = go.Figure(go.Bar(
            x=q_vals, y=q_labels, orientation="h",
            marker_color=[TEAL, AMBER, PURPLE, BLUE], opacity=0.85,
            text=[fmt_currency(v) for v in q_vals], textposition="outside",
            textfont=dict(size=12),
        ))
        fig3.update_layout(title="January Order Value — Quartile Breakdown",
                           showlegend=False)
        fig3.update_xaxes(tickprefix="$", tickformat=",.0f", title="Order Value ($)")
        fig3.update_yaxes(title="")
        base_layout(fig3, height=300)
        st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})

    st.markdown(f"""
    <div class="insight-box">
        <b>January AOV = {fmt_currency(jan_aov)}</b> (mean) vs
        <b>{fmt_currency(jan_median)}</b> (median) across {fmt_number(n_jan)} orders.
        The {fmt_currency(jan_aov - jan_median)} gap confirms right-skew — use median
        as the primary benchmark.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Q4: Day of week + Hour of day ─────────────────────────────────────────
    st.markdown('<p class="section-header">Q4 — Orders by Day of Week and Hour of Day</p>',
                unsafe_allow_html=True)

    work_df = revenue_df.copy()
    work_df["day_of_week"] = work_df["order_date"].dt.day_name()
    work_df["hour"]        = pd.to_datetime(work_df["order_datetime"], errors="coerce").dt.hour
    work_df["week"]        = work_df["order_date"].dt.isocalendar().week.astype(int)
    work_df["year"]        = work_df["order_date"].dt.year

    daily_counts = (
        work_df.groupby(["year", "week", "day_of_week"])["order_id"]
        .nunique().reset_index(name="n_orders")
    )
    avg_by_day = (
        daily_counts.groupby("day_of_week")["n_orders"]
        .mean().reindex(DAY_ORDER).reset_index()
    )
    peak_day = avg_by_day.loc[avg_by_day["n_orders"].idxmax()]

    hourly_counts = (
        work_df.dropna(subset=["hour"])
        .groupby(["order_date", "hour"])["order_id"]
        .nunique().reset_index(name="n_orders")
    )
    avg_by_hour = hourly_counts.groupby("hour")["n_orders"].mean().reset_index()
    peak_hour   = avg_by_hour.loc[avg_by_hour["n_orders"].idxmax()]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Busiest Day of Week",      peak_day["day_of_week"])
    c2.metric("Avg Orders on That Day",   f"{peak_day['n_orders']:.1f}")
    c3.metric("Busiest Hour",             f"{int(peak_hour['hour']):02d}:00")
    c4.metric("Avg Orders at That Hour",  f"{peak_hour['n_orders']:.1f}")

    col_c, col_d = st.columns(2)

    with col_c:
        colors = [TEAL if d == peak_day["day_of_week"] else "#A8D5D1"
                  for d in avg_by_day["day_of_week"]]
        fig4 = go.Figure(go.Bar(
            x=avg_by_day["day_of_week"],
            y=avg_by_day["n_orders"],
            marker_color=colors,
            opacity=0.90,
            text=[f"{v:.1f}" for v in avg_by_day["n_orders"]],
            textposition="outside",
            textfont=dict(size=12, color="#1A202C"),
            showlegend=False,
            hovertemplate="%{x}<br>Avg orders: <b>%{y:.1f}</b><extra></extra>",
        ))
        fig4.update_layout(title="Average Orders by Day of Week")
        fig4.update_yaxes(title="Avg Orders per Day")
        fig4.update_xaxes(title="Day of Week")
        base_layout(fig4, height=320)
        st.plotly_chart(fig4, use_container_width=True, config={"displayModeBar": False})

    with col_d:
        fig5 = go.Figure()
        fig5.add_scatter(
            x=avg_by_hour["hour"],
            y=avg_by_hour["n_orders"],
            mode="lines+markers",
            line=dict(color=AMBER, width=2.5),
            marker=dict(
                size=[14 if h == peak_hour["hour"] else 7 for h in avg_by_hour["hour"]],
                color=[TEAL if h == peak_hour["hour"] else AMBER for h in avg_by_hour["hour"]],
            ),
            showlegend=False,
            hovertemplate="%{x:02d}:00<br>Avg orders: <b>%{y:.1f}</b><extra></extra>",
        )
        fig5.add_annotation(
            x=peak_hour["hour"], y=peak_hour["n_orders"],
            text=f"Peak  {int(peak_hour['hour']):02d}:00",
            showarrow=True, arrowhead=2, arrowcolor=TEAL, arrowwidth=1.5,
            ax=36, ay=-40, font=dict(size=12, color="#1A202C"),
            bgcolor="white", bordercolor=TEAL, borderwidth=1, borderpad=4,
        )
        fig5.update_layout(title="Average Orders by Hour of Day")
        fig5.update_yaxes(title="Avg Orders per Hour")
        fig5.update_xaxes(
            tickvals=list(range(0, 24, 2)),
            ticktext=[f"{h:02d}:00" for h in range(0, 24, 2)],
            title="Hour of Day",
        )
        base_layout(fig5, height=320)
        st.plotly_chart(fig5, use_container_width=True, config={"displayModeBar": False})

    # Heatmap
    heat = (
        work_df.dropna(subset=["hour"])
        .groupby(["day_of_week", "hour"])["order_id"]
        .nunique().reset_index(name="n_orders")
    )
    heat_pivot = (
        heat.pivot(index="day_of_week", columns="hour", values="n_orders")
        .reindex(DAY_ORDER).fillna(0)
    )
    fig6 = go.Figure(go.Heatmap(
        z=heat_pivot.values,
        x=[f"{int(h):02d}:00" for h in heat_pivot.columns],
        y=heat_pivot.index,
        colorscale=[[0, "#EDF2F7"], [0.5, TEAL], [1, "#1A4A47"]],
        hovertemplate="%{y}  %{x}<br>Orders: <b>%{z}</b><extra></extra>",
        showscale=True,
        colorbar=dict(
            title=dict(text="Orders", font=dict(size=13, color=LABEL_COLOR)),
            thickness=14, len=0.8,
            tickfont=dict(size=11, color="#2D3748"),
        ),
    ))
    fig6.update_layout(title="Order Frequency — Day of Week x Hour of Day")
    fig6.update_xaxes(title="Hour of Day", tickangle=-45, tickfont=dict(size=11))
    fig6.update_yaxes(title="")
    base_layout(fig6, height=320)
    st.plotly_chart(fig6, use_container_width=True, config={"displayModeBar": False})

    st.markdown(f"""
    <div class="insight-box">
        <b>{peak_day["day_of_week"]}</b> is the busiest day with
        <b>{peak_day["n_orders"]:.1f} orders</b> on average.
        Peak hour is <b>{int(peak_hour["hour"]):02d}:00</b> with
        <b>{peak_hour["n_orders"]:.1f} orders</b> on average.
        Use the heatmap to target promotions and email send-times at
        high-traffic windows.
    </div>
    """, unsafe_allow_html=True)