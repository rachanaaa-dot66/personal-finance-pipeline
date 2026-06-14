# 🏦 Personal Finance Data Engineering Pipeline

An end-to-end Data Engineering, Analytics, and Business Intelligence project built using a Cambodia-realistic personal finance dataset.

This project demonstrates the complete data lifecycle: data generation, ETL processing, data warehousing, workflow orchestration, and interactive analytics dashboards.

---

## 🎯 Project Overview

This project simulates a real-world personal finance analytics platform for Cambodia. The pipeline generates over 1 million financial transactions, introduces realistic data quality issues, cleans and transforms the data using Apache Spark, loads the results into PostgreSQL, and delivers insights through Metabase, Streamlit, and Power BI dashboards.

---

## 🏗️ Architecture

```text
Python Data Simulation
          ↓
      Raw CSV Files (10 chunks)
          ↓
     combine_csv.py
          ↓
     PySpark ETL
          ↓
 PostgreSQL Warehouse
          ↓
 ┌──────────┬──────────┬──────────┐
 ↓          ↓          ↓          ↓
Metabase  Streamlit  Power BI  pgAdmin
Dashboard  App        Reports   DB View
 └──────────┴──────────┴──────────┘
                  ↓
          Apache Airflow
       Validation & Monitoring
```

---

## 🧱 Tech Stack

| Layer | Technology |
|---|---|
| Programming | Python |
| Data Processing | Apache Spark (PySpark) |
| Database | PostgreSQL |
| DB Management | pgAdmin 4 |
| Dashboarding | Metabase |
| Analytics App | Streamlit + Plotly |
| BI Reporting | Power BI |
| Workflow Orchestration | Apache Airflow |
| Containerization | Docker & Docker Compose |
| Version Control | Git & GitHub |

---

## 📂 Project Structure

```text
personal_finance_pipeline/
│
├── airflow/
│   └── dags/
│       └── finance_pipeline_dag.py     ← Airflow DAG
│
├── data/
│   ├── raw/                            ← 10 chunk CSVs (gitignored)
│   └── processed/
│       ├── transactions_raw_1M.csv     ← combined raw (gitignored)
│       ├── transactions_cleaned/       ← Spark output (gitignored)
│       ├── customers.csv
│       └── categories.csv
│
├── PowerBI/
│   ├── DE-Project-PowerBI.pbix         ← Power BI report file
│   └── Screenshot/
│       ├── Customers Insights.png
│       ├── Financial Overview.png
│       └── Spending Analysis.png
│
├── Screenshot/
│   ├── metabase-dashboard/
│   │   ├── financial overview.png
│   │   ├── spending analysis.png
│   │   ├── customer insight.png
│   │   ├── saving and income.png
│   │   ├── queries and dashboard.png
│   │   └── type of dashboard.png
│   ├── airflow page.png
│   ├── postgre-pgadmin.png
│   ├── postgre-query.png
│   ├── spark page.png
│   ├── streamlit-sample1.png
│   └── streamlit-sample2.png
│
├── scripts/
│   ├── simulation-categories.py        ← Generate categories reference
│   ├── simulation-customers.py         ← Generate 400 customers
│   ├── simulation-transactions.py      ← Generate 1M+ transactions
│   ├── combine_csv.py                  ← Merge 10 chunks into one
│   └── spark_etl.py                    ← PySpark ETL pipeline
│
├── sql/
│   └── init.sql                        ← PostgreSQL schema
│
├── streamlit_app.py                    ← Streamlit dashboard app
├── docker-compose.yml                  ← All services in one file
├── requirements.txt
└── README.md
```

---

## 🔄 Pipeline Workflow

### Step 1 — Data Simulation
Generate realistic Cambodian personal finance data including customer profiles, spending categories, and 1M+ financial transactions with intentional data quality issues.

### Step 2 — Data Quality Issues Injected

| Issue | Detail |
|---|---|
| Duplicate records | ~30,000 duplicate rows |
| Missing values | payment_method ~6%, sub_category ~6%, currency ~3% |
| Mixed date formats | ISO, DD/MM/YYYY, MM-DD-YYYY |
| Text noise | Mixed casing, extra whitespace |
| Invalid amounts | Negative values (~2%), zeros (~1%), comma-formatted strings |
| Location variants | `"phnom penh"`, `"PhnomPenh"`, `"Phnom-Penh"` |
| Age/income outliers | Invalid ages (0, 999), negative incomes |

### Step 3 — PySpark ETL
Clean, transform and load using Apache Spark:
- Remove 30,000 duplicate rows
- Standardise 3 date formats → standard DATE
- Normalize text casing across all fields
- Handle null values (fill with "Unknown"/"Uncategorised")
- Flag 59,448 anomalous amounts as `is_anomaly = true`
- Recalculate missing `amount_usd` from currency conversion
- Fix city name variants to canonical names
- Re-derive `spending_type` from categories reference table
- Load to PostgreSQL star schema

### Step 4 — Data Warehouse (PostgreSQL)
Star schema with 1 fact table and 2 dimension tables.

### Step 5 — Dashboards & Analytics
Business insights via Metabase, Streamlit, and Power BI.

### Step 6 — Airflow Validation
Automated warehouse validation with row count checks.

---

## 🗄️ Database Schema (Star Schema)

```
customers ──────────── transactions_cleaned ──────────── categories
(customer_id PK)       (customer_id FK)                 (sub_category PK)
                       (sub_category FK)
```

### customers (400 rows)
| Field | Type |
|---|---|
| customer_id | VARCHAR |
| name | VARCHAR |
| age | INT |
| gender | VARCHAR |
| marital_status | VARCHAR |
| city | VARCHAR |
| income_level | VARCHAR |
| monthly_income_usd | NUMERIC |
| occupation | VARCHAR |
| account_type | VARCHAR |
| customer_since | DATE |

### categories (64 rows)
| Field | Type |
|---|---|
| category | VARCHAR |
| sub_category | VARCHAR |
| spending_type | VARCHAR |

### transactions_cleaned (1,000,000 rows)
| Field | Type |
|---|---|
| transaction_id | VARCHAR |
| customer_id | VARCHAR |
| date | DATE |
| amount | NUMERIC |
| currency | VARCHAR |
| amount_usd | NUMERIC |
| category | VARCHAR |
| sub_category | VARCHAR |
| spending_type | VARCHAR |
| transaction_type | VARCHAR |
| payment_method | VARCHAR |
| notes | TEXT |
| is_anomaly | BOOLEAN |

---

## 📊 Dashboards

### Metabase (http://localhost:3000)
4 dashboards with 15+ charts:
- **Financial Overview** — KPIs, monthly trend
- **Spending Analysis** — categories, essential vs non-essential, payment methods
- **Customer Insights** — city, occupation, income level
- **Savings & Income** — savings trend, income sources, anomalies

### Streamlit (http://localhost:8501)
5-page interactive analytics app with filters:
- Date range, city, income level filters
- Financial Overview with KPI cards
- Spending Analysis with Plotly charts
- Customer Insights
- Savings & Income
- Data Quality Report

### Power BI
Professional BI reports connected to PostgreSQL:
- Financial Overview
- Customer Insights
- Spending Analysis

### pgAdmin (http://localhost:5051)
Database management and SQL query tool.

---

## ⏰ Apache Airflow (http://localhost:8088)

DAG: `personal_finance_pipeline`

```
truncate_postgres_tables
          ↓
    run_spark_etl
          ↓
  validate_row_counts
          ↓
   pipeline_complete
```

Validation checks:
- `transactions_cleaned >= 1,000,000`
- `customers = 400`
- `categories = 64`

---

## 📈 Key Results

| Metric | Value |
|---|---|
| Transactions generated | 1,030,000 |
| Duplicates removed | 30,000 |
| Clean transactions loaded | 1,000,000 |
| Anomalies flagged | 59,448 |
| Customers | 400 |
| Categories | 64 |
| Cities covered | 12 Cambodian cities |
| Total Income | $129.7M |
| Total Expense | $117.4M |
| Savings Rate | 9.5% |

---

## 🚀 How to Run

### 1. Generate Data
```bash
cd scripts
python simulation-categories.py
python simulation-customers.py
python simulation-transactions.py
python combine_csv.py
```

### 2. Start All Services
```bash
docker-compose up -d
```

Services started:
| Service | URL |
|---|---|
| Metabase | http://localhost:3000 |
| Streamlit | http://localhost:8501 |
| Airflow | http://localhost:8088 |
| Spark UI | http://localhost:8090 |
| pgAdmin | http://localhost:5051 |

### 3. Run PySpark ETL
```bash
docker exec spark-master /opt/spark/bin/spark-submit \
  --master spark://spark-master:7077 \
  --conf spark.jars.ivy=/tmp/.ivy2 \
  --packages org.postgresql:postgresql:42.6.0 \
  /opt/spark/scripts/spark_etl.py
```

### 4. Connect Power BI
- Server: `localhost:5433`
- Database: `finance_db`
- Username: `finance_user`
- Password: `finance_pass`

---

## 🇰🇭 Cambodia Context

- Dual currency economy (KHR + USD, rate: 4,100 KHR/USD)
- Cambodian payment methods: ABA Bank, ACLEDA, WING, Pi Pay, Bakong, TrueMoney
- Realistic Khmer names and 12-city distribution
- Occupation mapping by income level
- Spending patterns typical of Cambodian households

---

## 💡 Skills Demonstrated

- Data Engineering & ETL Development
- Apache Spark (PySpark) — Big Data Processing
- SQL & PostgreSQL — Data Warehousing
- Star Schema Design
- Docker & Docker Compose — Containerization
- Apache Airflow — Workflow Orchestration
- Metabase — Business Intelligence
- Streamlit + Plotly — Analytics App Development
- Power BI — BI Reporting
- Data Quality Engineering
- Git & GitHub — Version Control
- Python — Data Simulation & Processing

---

## 👨‍💻 Author

Developed as a final project to demonstrate modern Data Engineering, Analytics, and Business Intelligence workflows using open-source technologies with a focus on real-world Cambodian financial data.