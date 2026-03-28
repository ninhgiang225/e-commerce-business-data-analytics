# Sales Dashboard

An interactive Streamlit dashboard built on `dim_customers`, `dim_products`, and `fct_orders`.

## Setup

```bash
pip install -r requirements.txt
```

Place your three CSV files inside the `data_files/` folder:
```
data_files/
├── dim_customers.csv   # customer_id, country, state
├── dim_products.csv    # product_id, product_group
└── fct_orders.csv      # brand, item_id, gross_item_value, order_date, order_datetime, product_id, order_id, customer_id
```

## Run

```bash
streamlit run app.py
```

## Charts

| Chart | Description |
|---|---|
| **Monthly Revenue Trend** | Line chart of total gross_item_value aggregated by month |
| **Revenue by Brand** | Vertical bar chart of top 10 brands ranked by total revenue |
| **Revenue by Product Group** | Horizontal bar chart showing revenue per product group |
| **Top 10 Countries** | Horizontal bar chart of highest-revenue countries |
| **Geography & Brand Treemap** | Hierarchical view: Country → State → Brand by revenue |
| **Brand Performance Bubble** | Scatter of revenue vs. orders; bubble size = unique customers |

## Filters (sidebar)

- **Date range** — filter orders by order_date
- **Brand** — multi-select brand filter
- **Product Group** — multi-select product group filter
- **Country** — multi-select country filter
- **Reset** — clears all filters at once
