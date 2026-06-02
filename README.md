# 🏦 Personal Finance Data Engineering Pipeline

A complete end-to-end data engineering pipeline built with Cambodia-realistic financial transaction data.

---

## 🎯 Project Overview

This project simulates a real-world personal finance analytics platform for Cambodia, demonstrating a full modern data engineering stack — from raw data simulation through ETL processing, database storage, and interactive dashboard analytics.

---

## 🧱 Tech Stack

| Layer | Tool |
|---|---|
| Data Simulation | Python (Faker, Pandas, NumPy) |
| Big Data ETL | Apache Spark (PySpark) |
| Database | PostgreSQL |
| Visualization | Metabase |
| Containerization | Docker |
| Version Control | Git + GitHub |

---

## 📂 Project Structure

```
personal_finance_pipeline/
│
├── data/
│   ├── raw/                          # 10 raw transaction chunk CSVs (gitignored)
│   └── processed/                    # Cleaned output CSVs (gitignored)
│
├── scripts/
│   ├── simulation-categories.py      # Generate categories reference table
│   ├── simulation-customers.py       # Generate 400 Cambodian customers
│   ├── simulation-transactions.py    # Generate 1M+ transactions with messy data
│   ├── combine_csv.py                # Merge 10 chunk files into one
│   └── spark_etl.py                  # PySpark ETL — clean, transform, load to PostgreSQL
│
├── sql/
│   └── init.sql                      # PostgreSQL schema (auto-runs on container start)
│
├── docker-compose.yml                # Spark + PostgreSQL + Metabase
├── requirements.txt
└── README.md
```

---

## 🔄 Pipeline Workflow

```
Step 1 — Data Simulation (Python)
        ↓
Step 2 — Combine CSV chunks
        ↓
Step 3 — Spark ETL (clean + transform + load)
        ↓
Step 4 — PostgreSQL (star schema)
        ↓
Step 5 — Metabase Dashboards
```

---

## 🧪 Intentional Data Messiness (for ETL showcase)

The simulation intentionally injects real-world data quality issues:

| Issue | Detail |
|---|---|
| Mixed date formats | ISO, DD/MM/YYYY, MM-DD-YYYY |
| Amount formatting | Comma-separated strings e.g. `"1,250.00"` |
| Negative/zero amounts | ~3% of rows |
| Null values | payment_method ~6%, sub_category ~6%, currency ~3% |
| Casing noise | `"FOOD & BEVERAGE"`, `"food & beverage"`, `"Food & Beverage "` |
| Duplicate rows | ~3% double-submission simulation |
| City name variants | `"phnom penh"`, `"PhnomPenh"`, `"Phnom-Penh"` |
| Age/income outliers | Invalid ages (0, 999), negative incomes |

---

## 🧹 ETL Cleaning Steps (spark_etl.py)

- Remove ~30,000 duplicate rows via `dropDuplicates()`
- Standardise text casing with `initcap()` and `lower()`
- Parse 3 date formats → standard `DATE` type
- Strip comma formatting from amounts → cast to `DOUBLE`
- Flag anomalous amounts (negative/zero) as `is_anomaly = true`
- Recalculate missing `amount_usd` from currency + amount
- Fill nulls — `payment_method` → `"Unknown"`, `sub_category` → `"Uncategorised"`
- Fix city name variants → canonical names
- Re-derive `spending_type` from clean categories reference table
- Load 3 tables to PostgreSQL: `categories`, `customers`, `transactions_cleaned`

---

## 🗄️ Database Schema (Star Schema)

```
        customers
            │
            │ customer_id
            │
transactions_cleaned ──── categories
                          sub_category
```

**Fact table:** `transactions_cleaned` (1,000,000 rows)
**Dimension tables:** `customers` (400 rows), `categories` (64 rows)

---

## 📊 Metabase Dashboards

### 1. Financial Overview
- Total Income KPI: **$129.7M**
- Total Expense KPI: **$117.4M**
- Total Anomalies: **59,448**
- Monthly Income vs Expense trend (line chart)

### 2. Spending Analysis
- Spending by Category (bar chart)
- Essential vs Non-Essential (pie chart — 67% / 33%)
- Top 10 Sub-categories
- Payment Method breakdown (ABA Bank, Cash KHR/USD, ACLEDA, WING)

### 3. Customer Insights
- Spending by City (Phnom Penh dominant)
- Spending by Occupation
- Customer distribution by Income Level
- Avg spend per customer by Income Level

### 4. Savings & Income
- Monthly Savings Trend (~$900K/month)
- Income by Type (7 income sources)
- Anomalies by Category

---

## 🚀 How to Run

### Prerequisites
- Docker Desktop installed
- Python 3.8+

### 1. Generate simulation data
```bash
cd scripts
python simulation-categories.py
python simulation-customers.py
python simulation-transactions.py
python combine_csv.py
```

### 2. Start all services
```bash
docker-compose up -d
```

### 3. Run Spark ETL
```bash
docker exec spark-master /opt/spark/bin/spark-submit \
  --master spark://spark-master:7077 \
  --conf spark.jars.ivy=/tmp/.ivy2 \
  --packages org.postgresql:postgresql:42.6.0 \
  /opt/spark/scripts/spark_etl.py
```

### 4. Open Metabase
Go to `http://localhost:3000` and connect to:
- Host: `postgres`
- Port: `5432`
- Database: `finance_db`
- Username: `finance_user`
- Password: `finance_pass`

---

## 📈 Key Results

| Metric | Value |
|---|---|
| Total transactions generated | 1,030,000 |
| Duplicates removed | 30,000 |
| Anomalous amounts flagged | 59,448 |
| Clean rows loaded to PostgreSQL | 1,000,000 |
| Total Income | $129.7M |
| Total Expense | $117.4M |
| Customers | 400 |
| Cities covered | 12 Cambodian cities |

---

## 🇰🇭 Cambodia Context

- Dual currency economy (KHR + USD)
- Cambodian payment methods: ABA Bank, ACLEDA, WING, Pi Pay, Bakong, TrueMoney
- Realistic Khmer names and city distribution
- Income levels reflecting Cambodia's economic structure
- Spending patterns typical of Cambodian households