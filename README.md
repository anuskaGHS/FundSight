# FundSight — Indian Startup Funding Analytics Dashboard

> An end-to-end data analytics project analysing 3,000+ Indian startup funding records (2010–2025) across sectors, cities, and funding stages.

---

## Live Dashboard

🔗 [View on Streamlit Cloud](#) *(link will be updated after deployment)*

---

## Project Overview

FundSight is a full-stack data analytics portfolio project built to uncover trends in Indian startup funding over 15 years. It covers the complete data analyst workflow — from raw data ingestion and cleaning, through SQL-based analysis, to an interactive multi-page dashboard.

### Key Insights
- Peak funding activity recorded in **2016** with 987 deals
- **Bangalore** leads all cities with 28% of total deal volume
- **Bangalore + Delhi NCR** together account for ~60% of all deals
- **Consumer Internet** dominates sector-wise with 927 deals (2010–2025)
- **Fintech** showed strong growth from 2016–2018

---

## Tech Stack

| Layer | Tools |
|---|---|
| Data Cleaning | Python, Pandas |
| Database | MySQL |
| SQL Analysis | MySQL Workbench |
| Visualisation | Plotly, Matplotlib, Seaborn |
| Dashboard | Streamlit |
| Deployment | Streamlit Cloud |
| Version Control | Git, GitHub |

---

## Dataset

Two Kaggle datasets merged and cleaned:

1. **Indian Startup Funding** by Sudalai Rajkumar (SRK) — ~3,000 records, 2015–2020
   - [kaggle.com/datasets/sudalairajkumar/indian-startup-funding](https://www.kaggle.com/datasets/sudalairajkumar/indian-startup-funding)

2. **Indian Startup Funding Dataset 2010–2025** by Nikita — 200 records
   - [kaggle.com/datasets/nikitagajbhiye30/indian-startup-funding-dataset-20102025](https://www.kaggle.com/datasets/nikitagajbhiye30/indian-startup-funding-dataset-20102025)

**Final cleaned dataset:** 3,196 records · 7 columns · 2010–2025

---

## Project Structure

```
FundSight/
│
├── data/
│   ├── SRK_startup_funding.csv         ← raw dataset 1
│   ├── 2010-2025_startup_funding.csv   ← raw dataset 2
│   └── cleaned_startup_funding.csv     ← output of cleaning script
│
├── notebooks/
│   ├── 03_eda.py                        ← EDA visualisations
│   └── charts/                          ← saved chart PNGs
│
├── sql/
│   └── business_insights.sql            ← all SQL queries
│
├── dashboard/
│   ├── app.py                           ← Overview page
│   ├── style.css                        ← shared CSS
│   └── pages/
│       ├── 1_Sector_Analysis.py
│       ├── 2_City_Analysis.py
│       ├── 3_Funding_Stages.py
│       └── 4_Data_Explorer.py
│
├── 01_data_cleaning.py                  ← data cleaning script
├── 02_load_to_mysql.py                  ← MySQL loader script
├── requirements.txt
└── README.md
```

---

## Dashboard Pages

| Page | Description |
|---|---|
| **Overview** | KPI metrics, year-wise trend, top sectors & cities |
| **Sector Analysis** | Sector breakdown, heatmap, Fintech growth, funding amounts |
| **City Analysis** | City rankings, Bangalore vs Delhi NCR, city × sector matrix |
| **Funding Stages** | Stage distribution, trends over time, avg deal sizes |
| **Data Explorer** | Searchable, filterable raw data table with CSV export |

---

## How to Run Locally

### Prerequisites
- Python 3.10+
- MySQL Community Server
- Git

### Setup

```bash
# 1. Clone the repo
git clone https://github.com/anuskaGHS/FundSight.git
cd FundSight

# 2. Create virtual environment
python -m venv venv
venv\Scripts\Activate.ps1   # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file in root
# DB_HOST=localhost
# DB_USER=root
# DB_PASSWORD=your_password
# DB_NAME=fundsight

# 5. Run data cleaning
python 01_data_cleaning.py

# 6. Load data into MySQL
python 02_load_to_mysql.py

# 7. Launch dashboard
streamlit run dashboard/app.py
```

---

## SQL Queries

The `sql/business_insights.sql` file contains 8 analytical queries:

1. Total deals and funding by sector
2. Year-wise funding trend (2010–2025)
3. City-wise deal volume and % share
4. Funding stage distribution
5. Post-2020 sector analysis
6. Year-over-year growth (window function)
7. Bangalore vs Delhi NCR head-to-head
8. Top 15 funded startups

---

## Author

**Anuska Ghosh**

---

*Data Source: Kaggle · Built with Python, SQL & Streamlit*
