# Atomic Data Analyst Exercise

## Deliverables
- 👉 Live App: [streamlit app](https://atomic-e-commerce-analytics.streamlit.app/)
- 👉 Executive Summary: [a page](https://github.com/ninhgiang225/e-commerce-business-data-analytics/blob/main/docs/Executive%20summary_%20E-commerce%20Performance%20Audit%20copy.pdf)
- 👉 Data Quality check: [notebook](https://github.com/ninhgiang225/e-commerce-business-data-analytics/blob/main/notebooks/data_quality_check.ipynb)
   
<img width="1046" height="749" alt="image" src="https://github.com/user-attachments/assets/04765cbb-a0b3-4642-9663-c06324a3cafa" />
<img width="1028" height="730" alt="image" src="https://github.com/user-attachments/assets/d3cff444-fdab-4e8d-a42b-d3c3e9625dae" />


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
- Data quality check and cleaning
- Dataset joins (`item_id`, `product_id`, `customer_id`)  
- Feature engineering (date, weekday, hour, order value)  
- Aggregations and grouping  
- Statistical testing (for category comparison)  
- Data visualization
- Dashboarding deployment by streamlit  

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
streamlit run app.py
