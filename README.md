# 🏦 Personal Finance Data Engineering Pipeline

An end-to-end Data Engineering, Analytics, and Business Intelligence project built using a Cambodia-realistic personal finance dataset.

This project demonstrates the complete data lifecycle: data generation, ETL processing, data warehousing, workflow orchestration, and interactive analytics dashboards.

---

# 🎯 Project Overview

This project simulates a real-world personal finance analytics platform for Cambodia.

The pipeline generates over 1 million financial transactions, introduces realistic data quality issues, cleans and transforms the data using Apache Spark, loads the results into PostgreSQL, validates the warehouse using Apache Airflow, and delivers insights through Metabase and Streamlit dashboards.

---

# 🏗️ Architecture

```text
Python Data Simulation
          ↓
      Raw CSV Files
          ↓
     PySpark ETL
          ↓
 PostgreSQL Warehouse
          ↓
 ┌───────────────────┬───────────────────┐
 │                   │
 ↓                   ↓
Metabase        Streamlit
Dashboard       Analytics App
 │                   │
 └─────────┬─────────┘
           ↓
Apache Airflow
Validation & Monitoring
```

---

# 🧱 Tech Stack

| Layer                  | Technology              |
| ---------------------- | ----------------------- |
| Programming            | Python                  |
| Data Processing        | Apache Spark (PySpark)  |
| Database               | PostgreSQL              |
| Dashboarding           | Metabase                |
| Analytics App          | Streamlit               |
| Workflow Orchestration | Apache Airflow          |
| Containerization       | Docker & Docker Compose |
| Version Control        | Git & GitHub            |

---

# 📂 Project Structure

```text
personal_finance_pipeline/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── scripts/
│   ├── simulation-categories.py
│   ├── simulation-customers.py
│   ├── simulation-transactions.py
│   ├── combine_csv.py
│   └── spark_etl.py
│
├── airflow/
│   └── dags/
│       └── finance_pipeline_dag.py
│
├── sql/
│   └── init.sql
│
├── streamlit_app.py
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

# 🔄 Pipeline Workflow

### Step 1 — Data Simulation

Generate realistic Cambodian personal finance data:

* Customer profiles
* Spending categories
* Financial transactions
* Income and savings records

### Step 2 — Data Quality Issues Injection

The simulation intentionally introduces:

* Duplicate records
* Missing values
* Mixed date formats
* Currency inconsistencies
* Text formatting issues
* Invalid values and anomalies

### Step 3 — PySpark ETL

Process and clean raw data using Apache Spark:

* Remove duplicates
* Standardize dates
* Normalize text fields
* Handle null values
* Detect anomalies
* Generate derived attributes
* Load clean data into PostgreSQL

### Step 4 — Data Warehouse

Store cleaned data in PostgreSQL using a star-schema design.

### Step 5 — Dashboard & Analytics

Provide business insights through:

* Metabase dashboards
* Streamlit analytics application

### Step 6 — Airflow Validation

Validate warehouse quality using automated checks.

---

# 🧪 Simulated Data Quality Issues

| Issue                  | Description                             |
| ---------------------- | --------------------------------------- |
| Duplicate Transactions | ~30,000 duplicate records               |
| Missing Values         | Payment methods, categories, currencies |
| Mixed Date Formats     | Multiple date representations           |
| Text Noise             | Inconsistent casing and spacing         |
| Currency Variations    | USD and KHR values                      |
| Invalid Values         | Negative and zero amounts               |
| Location Variations    | Multiple city name formats              |
| Outliers               | Extreme age and income values           |

---

# 🧹 ETL Processing

The PySpark ETL pipeline performs:

### Data Cleaning

* Remove duplicate transactions
* Standardize text formats
* Normalize city names
* Convert dates to standard format
* Clean amount fields

### Data Transformation

* Currency conversion
* Spending type classification
* Category mapping
* Derived feature creation

### Data Quality Validation

* Missing value handling
* Anomaly detection
* Data consistency checks

---

# 🗄️ Data Warehouse Schema

### customers

Stores customer demographic information.

| Field              |
| ------------------ |
| customer_id        |
| name               |
| age                |
| gender             |
| city               |
| occupation         |
| income_level       |
| monthly_income_usd |

---

### categories

Stores spending classifications.

| Field         |
| ------------- |
| category      |
| sub_category  |
| spending_type |

---

### transactions_cleaned

Stores cleaned transactional data.

| Field            |
| ---------------- |
| transaction_id   |
| customer_id      |
| date             |
| amount           |
| currency         |
| amount_usd       |
| category         |
| sub_category     |
| spending_type    |
| transaction_type |
| payment_method   |
| is_anomaly       |

---

# 📊 Metabase Dashboards

## Financial Overview

Features:

* Total Income
* Total Expenses
* Savings Rate
* Monthly Trends
* Anomaly Summary

## Spending Analysis

Features:

* Spending by Category
* Essential vs Non-Essential Spending
* Top Spending Categories
* Payment Method Analysis

## Customer Insights

Features:

* Spending by City
* Spending by Occupation
* Income Level Distribution
* Customer Segmentation

## Savings & Income Analysis

Features:

* Savings Trends
* Income Sources
* Income-Level Comparisons

---

# 📈 Streamlit Analytics Dashboard

Interactive dashboard built using Streamlit and Plotly.

### Features

* Date range filtering
* City filtering
* Income-level filtering
* KPI cards
* Interactive charts
* Customer insights
* Spending analytics
* Data quality monitoring

### Pages

1. Financial Overview
2. Spending Analysis
3. Customer Insights
4. Savings & Income
5. Data Quality Report

---

# ⏰ Apache Airflow Workflow

Airflow is used for:

* Warehouse validation
* Data quality monitoring
* Pipeline execution visibility

### Validation Checks

```text
transactions_cleaned >= 1,000,000
customers = 400
categories = 64
```

Successful execution confirms warehouse integrity.

---

# 📈 Key Results

| Metric                    | Value     |
| ------------------------- | --------- |
| Transactions Generated    | 1,030,000 |
| Duplicates Removed        | 30,000    |
| Clean Transactions Loaded | 1,000,000 |
| Customers                 | 400       |
| Categories                | 64        |
| Supported Cities          | 12        |
| Anomalies Flagged         | 59,448    |

---

# 🚀 How to Run

## 1. Generate Data

```bash
cd scripts

python simulation-categories.py
python simulation-customers.py
python simulation-transactions.py
python combine_csv.py
```

## 2. Start Infrastructure

```bash
docker-compose up -d
```

## 3. Run PySpark ETL

```bash
docker exec spark-master /opt/spark/bin/spark-submit \
--master spark://spark-master:7077 \
--conf spark.jars.ivy=/tmp/.ivy2 \
--packages org.postgresql:postgresql:42.6.0 \
/opt/spark/scripts/spark_etl.py
```

## 4. Launch Streamlit

```bash
streamlit run streamlit_app.py
```

## 5. Open Dashboards

### Metabase

```text
http://localhost:3000
```

### Streamlit

```text
http://localhost:8501
```

### Spark Master UI

```text
http://localhost:8090
```

### Airflow

```text
http://localhost:8080
```

---

# 📷 Dashboard Screenshots

Add screenshots here:

```text
screenshots/
├── airflow_pipeline.png
├── metabase_dashboard.png
├── streamlit_dashboard.png
```

---

# 💡 Skills Demonstrated

* Data Engineering
* ETL Development
* Apache Spark (PySpark)
* SQL
* PostgreSQL
* Data Warehousing
* Docker
* Apache Airflow
* Business Intelligence
* Dashboard Development
* Streamlit
* Data Quality Validation
* Git & GitHub

---

# 👨‍💻 Author

Developed as a portfolio project to demonstrate modern Data Engineering, Analytics, and Business Intelligence workflows using open-source technologies.
