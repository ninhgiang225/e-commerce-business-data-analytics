# Atomic Data Analyst Exercise
<p>
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white"/>
  <img src="https://img.shields.io/badge/NumPy-013243?style=for-the-badge&logo=numpy&logoColor=white"/>
  <img src="https://img.shields.io/badge/SciPy-8CAAE6?style=for-the-badge&logo=scipy&logoColor=white"/>
  <img src="https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white"/>
  <img src="https://img.shields.io/badge/Seaborn-4C9BE8?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Matplotlib-11557C?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white"/>
  <img src="https://img.shields.io/badge/Jupyter-F37626?style=for-the-badge&logo=jupyter&logoColor=white"/>
  <img src="https://img.shields.io/badge/IQR%20Outlier%20Detection-2BBFB3?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Welch's%20t--test-7B5EA7?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Winsorization-F5A623?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Rolling%20Average-5DB87A?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Data%20Quality%20Audit-E8607A?style=for-the-badge"/>
</p>

## Deliverables
- 👉 Live App: [streamlit app](https://atomic-e-commerce-analytics.streamlit.app/)
- 👉 Executive Summary: [a page](https://github.com/ninhgiang225/e-commerce-business-data-analytics/blob/main/docs/Executive%20summary_%20E-commerce%20Performance%20Audit.pdf)
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
