import pandas as pd
import streamlit as st
from pathlib import Path

REQUIRED_COLS = [
    "brand", "item_id", "gross_item_value", "order_date", "order_datetime",
    "product_id", "order_id", "customer_id", "product_group", "country", "state",
]

DATA_PATH = Path(__file__).parent.parent / "data_files" / "master_table.csv"


@st.cache_data
def load_data() -> pd.DataFrame:
    if not DATA_PATH.exists():
        st.error(f"master_table.csv not found at: {DATA_PATH}")
        st.stop()

    df = pd.read_csv(DATA_PATH)

    # ── Parse dates ──────────────────────────────────────────────────────────
    df["order_date"]     = pd.to_datetime(df["order_date"], infer_datetime_format=True, errors="coerce").dt.normalize()
    df["order_datetime"] = pd.to_datetime(df["order_datetime"], infer_datetime_format=True, errors="coerce")

    # ── Normalise string cols ─────────────────────────────────────────────────
    for col in ["brand", "product_group", "country", "state"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    # ── customer_id: scientific notation fix ─────────────────────────────────
    if df["customer_id"].dtype == float:
        df["customer_id"] = df["customer_id"].astype("Int64").astype(str)

    # ── Data-quality flags ───────────────────────────────────────────────────
    df["is_promo_zero"] = (
        (df["gross_item_value"] == 0.0) &
        (df["brand"].isin(["Brand 2", "Brand 3"])) &
        (df["product_group"] == "Category 8")
    )
    df["is_data_error"] = df["gross_item_value"] < 0
    df["value_clean"]   = df["gross_item_value"].clip(lower=0)  # used in visualisations

    return df