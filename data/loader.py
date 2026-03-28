"""Data loading, parsing and joining — all caching lives here."""
from pathlib import Path

import pandas as pd
import streamlit as st

DATA_DIR = Path(__file__).parent.parent / "data_files"

# ── Column name constants ─────────────────────────────────────────────────────
COL_CUSTOMER_ID   = "customer_id"
COL_PRODUCT_ID    = "product_id"
COL_ORDER_ID      = "order_id"
COL_ITEM_ID       = "item_id"
COL_ORDER_DATE    = "order_date"
COL_ORDER_DT      = "order_datetime"
COL_GROSS_VALUE   = "gross_item_value"
COL_BRAND         = "brand"
COL_COUNTRY       = "country"
COL_STATE         = "state"
COL_PRODUCT_GROUP = "product_group"


@st.cache_data(ttl=600, show_spinner=False)
def _load_raw(filename: str) -> pd.DataFrame:
    """Load a single CSV from DATA_DIR.

    Args:
        filename: CSV filename (e.g. 'fct_orders.csv').

    Returns:
        Raw DataFrame, or empty DataFrame on error.
    """
    path = DATA_DIR / filename
    try:
        return pd.read_csv(path)
    except FileNotFoundError:
        st.error(f"❌ File not found: `{path}`. Place your CSVs in `data_files/`.")
        return pd.DataFrame()
    except Exception as exc:  # noqa: BLE001
        st.error(f"❌ Error reading `{filename}`: {exc}")
        return pd.DataFrame()


@st.cache_data(ttl=600, show_spinner=False)
def load_all_data() -> dict[str, pd.DataFrame]:
    """Load, parse and join all three CSVs.

    Returns:
        Dict with keys 'orders', 'customers', 'products'.
        'orders' is the enriched fact table joined with both dimensions.
    """
    orders    = _load_raw("fct_orders.csv")
    customers = _load_raw("dim_customers.csv")
    products  = _load_raw("dim_products.csv")

    if orders.empty:
        return {"orders": pd.DataFrame(), "customers": customers, "products": products}

    # ── Parse datetimes ───────────────────────────────────────────────────────
    if COL_ORDER_DT in orders.columns:
        orders[COL_ORDER_DT] = pd.to_datetime(orders[COL_ORDER_DT], errors="coerce")

    if COL_ORDER_DATE in orders.columns:
        orders[COL_ORDER_DATE] = pd.to_datetime(orders[COL_ORDER_DATE], errors="coerce")
    elif COL_ORDER_DT in orders.columns:
        orders[COL_ORDER_DATE] = orders[COL_ORDER_DT].dt.normalize()

    # ── Derived time columns (needed for Q4) ──────────────────────────────────
    if COL_ORDER_DT in orders.columns:
        orders["day_of_week"] = orders[COL_ORDER_DT].dt.day_name()
        orders["hour_of_day"] = orders[COL_ORDER_DT].dt.hour
    elif COL_ORDER_DATE in orders.columns:
        orders["day_of_week"] = orders[COL_ORDER_DATE].dt.day_name()

    # ── Numeric coercion ──────────────────────────────────────────────────────
    if COL_GROSS_VALUE in orders.columns:
        orders[COL_GROSS_VALUE] = pd.to_numeric(orders[COL_GROSS_VALUE], errors="coerce").fillna(0.0)

    # ── Join dimensions ───────────────────────────────────────────────────────
    if not customers.empty and COL_CUSTOMER_ID in orders.columns:
        orders = orders.merge(customers, on=COL_CUSTOMER_ID, how="left")

    if not products.empty and COL_PRODUCT_ID in orders.columns:
        orders = orders.merge(products, on=COL_PRODUCT_ID, how="left")

    return {"orders": orders, "customers": customers, "products": products}