# Atomic Data Analyst Exercise

## Overview
This project analyzes e-commerce data to generate business insights using three datasets:
- **Order Items** – item-level transaction data  
- **Products** – product attributes (brand, category)  
- **Customers** – customer details (e.g., location)  

---

## Questions Answered
- Total Order Value by day (visualization)  
- Average Order Value (AOV) in January  
- Top brand in Texas by total order value  
- Most active:
  - Day of the week (avg. orders)  
  - Hour of the day  
- Product category with highest avg. gross item value  
  - Statistical significance vs. next category  
- Additional insights  

---

## Methodology
- Data cleaning and validation  
- Dataset joins (`order_id`, `product_id`, `customer_id`)  
- Feature engineering (date, weekday, hour, order value)  
- Aggregations and grouping  
- Statistical testing (for category comparison)  
- Data visualization with Dashboarding 

---

## Tools
- Python (Pandas, NumPy)  
- Matplotlib / Seaborn  
- SciPy / Statsmodels  
- Jupyter Notebook  

---

## How to Run
```bash
git clone https://github.com/your-username/atomic-data-analyst-exercise.git
pip install -r requirements.txt
jupyter notebook
