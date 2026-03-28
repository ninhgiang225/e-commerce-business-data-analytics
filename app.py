"""E-Commerce Analytics Dashboard — answers 5 analyst exercise questions."""
from pathlib import Path

import streamlit as st

from data.loader import load_all_data
from components.filters import render_sidebar_filters
from components.kpi_cards import render_kpi_row
from components.charts import (
    render_q1_daily_order_value,
    render_q2_january_aov,
    render_q3_texas_brands,
    render_q4_day_hour_patterns,
    render_q5_category_analysis,
    render_bonus_insights,
)

st.set_page_config(
    page_title="E-Commerce Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

_CSS = """
<style>
[data-testid="stMetric"] {
    background: #F2F4F8;
    border: 1px solid rgba(14,165,233,0.15);
    border-top: 3px solid #0EA5E9;
    border-radius: 10px;
    padding: 18px 22px !important;
}
[data-testid="stMetricValue"]  { font-size: 1.65rem !important; font-weight: 700; }
[data-testid="stMetricDelta"]  { font-size: 0.8rem !important; }
[data-testid="stPlotlyChart"]  {
    border-radius: 10px;
    border: 1px solid rgba(0,0,0,0.06);
    padding: 6px;
    background: #fff;
}
[data-testid="stSidebar"] { background: #F2F4F8; border-right: 1px solid rgba(0,0,0,0.07); }
.question-header {
    background: linear-gradient(90deg, #0EA5E9 0%, #38BDF8 100%);
    color: white;
    padding: 10px 18px;
    border-radius: 8px;
    font-weight: 700;
    font-size: 1rem;
    margin-bottom: 0.75rem;
}
.insight-box {
    background: #F0F9FF;
    border-left: 4px solid #0EA5E9;
    padding: 12px 16px;
    border-radius: 0 8px 8px 0;
    font-size: 0.9rem;
    margin-top: 0.5rem;
}
#MainMenu, footer, header { visibility: hidden; }
</style>
"""
st.markdown(_CSS, unsafe_allow_html=True)


def main() -> None:
    """Render the full dashboard."""
    st.markdown("# 📊 E-Commerce Analytics Dashboard")
    st.caption("Atomic Data Analyst Exercise — Order Items · Products · Customers")
    st.divider()

    with st.spinner("Loading and joining data…"):
        data = load_all_data()

    if data["orders"].empty:
        st.error("Could not load data. Place your CSVs in the `data_files/` folder.")
        return

    filtered = render_sidebar_filters(data)

    if filtered["orders"].empty:
        st.warning("⚠️ No data matches the current filters.")
        return

    render_kpi_row(filtered)
    st.divider()

    # ── Q1 ────────────────────────────────────────────────────────────────────
    st.markdown('<div class="question-header">Q1 · Total Order Value by Day</div>', unsafe_allow_html=True)
    render_q1_daily_order_value(filtered)
    st.divider()

    # ── Q2 ────────────────────────────────────────────────────────────────────
    st.markdown('<div class="question-header">Q2 · Average Order Value in January</div>', unsafe_allow_html=True)
    render_q2_january_aov(filtered)
    st.divider()

    # ── Q3 ────────────────────────────────────────────────────────────────────
    st.markdown('<div class="question-header">Q3 · Highest Total Order Value by Brand in Texas</div>', unsafe_allow_html=True)
    render_q3_texas_brands(filtered)
    st.divider()

    # ── Q4 ────────────────────────────────────────────────────────────────────
    st.markdown('<div class="question-header">Q4 · Orders by Day of Week & Hour of Day</div>', unsafe_allow_html=True)
    render_q4_day_hour_patterns(filtered)
    st.divider()

    # ── Q5 ────────────────────────────────────────────────────────────────────
    st.markdown('<div class="question-header">Q5 · Product Category with Highest Avg Gross Item Value + Statistical Test</div>', unsafe_allow_html=True)
    render_q5_category_analysis(filtered)
    st.divider()

    # ── Bonus ─────────────────────────────────────────────────────────────────
    st.markdown('<div class="question-header">💡 Bonus Insights</div>', unsafe_allow_html=True)
    render_bonus_insights(filtered)

    st.divider()
    with st.expander("📋 Raw Orders Data", expanded=False):
        st.dataframe(filtered["orders"], use_container_width=True, hide_index=True)
        st.download_button(
            "⬇️ Download filtered CSV",
            data=filtered["orders"].to_csv(index=False),
            file_name="filtered_orders.csv",
            mime="text/csv",
        )


if __name__ == "__main__":
    main()