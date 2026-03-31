import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from utils.charts import base_layout, fmt_currency, fmt_number, TEAL, AMBER, PURPLE


def render(df: pd.DataFrame, revenue_df: pd.DataFrame) -> None:
    st.markdown("## Customer Analysis")

    total_customers  = revenue_df["customer_id"].nunique()
    orders_per_cust  = revenue_df.groupby("customer_id")["order_id"].nunique()
    repeat_customers = (orders_per_cust > 1).sum()
    repeat_rate      = repeat_customers / total_customers * 100
    avg_orders       = orders_per_cust.mean()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Unique Customers",       fmt_number(total_customers))
    c2.metric("Repeat Customers",       fmt_number(repeat_customers))
    c3.metric("Repeat Rate",            f"{repeat_rate:.1f}%")
    c4.metric("Avg Orders / Customer",  f"{avg_orders:.2f}")

    st.markdown("---")

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown('<p class="section-header">Orders per Customer</p>', unsafe_allow_html=True)
        opc = orders_per_cust.value_counts().sort_index().reset_index()
        opc.columns = ["n_orders", "n_customers"]
        opc = opc[opc["n_orders"] <= 10]

        fig = go.Figure(go.Bar(
            x=opc["n_orders"].astype(str),
            y=opc["n_customers"],
            marker_color=TEAL,
            opacity=0.85,
            hovertemplate="Orders: %{x}<br>Customers: <b>%{y}</b><extra></extra>",
        ))
        fig.update_layout(title="How Many Orders Does Each Customer Place?")
        fig.update_xaxes(title="Number of Orders")
        fig.update_yaxes(title="Number of Customers")
        base_layout(fig, height=300)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with col_b:
        st.markdown('<p class="section-header">Customer Revenue Distribution</p>',
                    unsafe_allow_html=True)
        cust_rev = revenue_df.groupby("customer_id")["gross_item_value"].sum().reset_index()
        p99      = cust_rev["gross_item_value"].quantile(0.99)
        plot_cr  = cust_rev[cust_rev["gross_item_value"] <= p99]

        fig2 = go.Figure(go.Histogram(
            x=plot_cr["gross_item_value"],
            nbinsx=30,
            marker_color=AMBER,
            opacity=0.85,
        ))
        fig2.update_layout(title="Total Spend per Customer (1st–99th pct)")
        fig2.update_xaxes(tickprefix="$", tickformat=",.0f", title="Total Spend ($)")
        fig2.update_yaxes(title="Number of Customers")
        base_layout(fig2, height=300)
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

    st.markdown("---")

    st.markdown('<p class="section-header">Top 15 Customers by Revenue</p>',
                unsafe_allow_html=True)

    top_custs = (
        revenue_df.groupby("customer_id")
        .agg(
            total_revenue=("gross_item_value", "sum"),
            total_orders=("order_id",  "nunique"),
            total_items=("item_id",   "count"),
            avg_item_value=("gross_item_value", "mean"),
        )
        .sort_values("total_revenue", ascending=False)
        .head(15)
        .reset_index()
    )

    col_c, col_d = st.columns([2, 1])

    with col_c:
        fig3 = go.Figure(go.Bar(
            x=top_custs["total_revenue"],
            y=top_custs["customer_id"].astype(str),
            orientation="h",
            marker_color=PURPLE,
            opacity=0.85,
            hovertemplate="%{y}<br><b>$%{x:,.0f}</b><extra></extra>",
        ))
        fig3.update_layout(title="Top 15 Customers — Total Revenue")
        fig3.update_xaxes(tickprefix="$", tickformat=",.0f", title="Revenue ($)")
        fig3.update_yaxes(title="")
        base_layout(fig3, height=360)
        st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})

    with col_d:
        display = top_custs.copy()
        display["total_revenue"]  = display["total_revenue"].map(fmt_currency)
        display["avg_item_value"] = display["avg_item_value"].map(fmt_currency)
        display["customer_id"]    = display["customer_id"].astype(str).str[:10] + "..."
        st.dataframe(
            display.rename(columns={
                "customer_id":    "Customer",
                "total_revenue":  "Revenue",
                "total_orders":   "Orders",
                "total_items":    "Items",
                "avg_item_value": "Avg $",
            }),
            use_container_width=True,
            hide_index=True,
            height=360,
        )