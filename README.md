# Personal Finance Analytics Pipeline

## Overview

An end-to-end data engineering and analytics project that simulates personal finance transactions, processes data using PySpark, stores cleaned data in PostgreSQL, and visualizes insights through Metabase dashboards.

This project demonstrates skills in data generation, ETL development, data warehousing, containerization, and business intelligence reporting.

## Tech Stack

* Python
* PySpark
* PostgreSQL
* Docker & Docker Compose
* Metabase
* SQL
* Git & GitHub

## Project Architecture

Raw Data Generation
→ Data Cleaning & Transformation (PySpark)
→ PostgreSQL Data Warehouse
→ Metabase Dashboards

## Dataset

### Customers

* 400 simulated customers
* Demographic information
* Income levels
* Account details

### Transactions

* 1,030,000 generated transactions
* 30,000 duplicate records intentionally inserted
* Multiple payment methods
* Multiple spending categories

### Categories

* 64 spending sub-categories
* Essential and Non-Essential spending classification

## ETL Process

### Data Quality Checks

* Duplicate removal
* Date standardization
* Text normalization
* Missing value handling
* Currency standardization
* Anomaly detection

### Data Enrichment

* Category mapping
* Spending type derivation
* Customer profile integration

## Database Schema

### customers

Stores customer demographic and account information.

### categories

Stores category and spending classification information.

### transactions_cleaned

Stores cleaned and transformed transaction records.

## Results

### Final Dataset

* Transactions: 1,000,000
* Customers: 400
* Categories: 64

### Data Quality Improvements

* Removed 30,000 duplicate transactions
* Standardized inconsistent formats
* Flagged anomalous transactions
* Recovered missing values

## Dashboards

### Executive Dashboard

* Total Spending
* Total Transactions
* Customer Count

### Spending Analysis Dashboard

* Spending by Category
* Spending Trends
* Payment Method Analysis

### Anomaly Monitoring Dashboard

* Anomalous Transaction Detection
* High-Risk Customer Identification

## How to Run

```bash
docker-compose up -d
```

```bash
docker exec spark-master /opt/spark/bin/spark-submit \
--master spark://spark-master:7077 \
--conf spark.jars.ivy=/tmp/.ivy2 \
--packages org.postgresql:postgresql:42.6.0 \
/opt/spark/scripts/spark_etl.py
```

Open Metabase:

http://localhost:3000

## Author

Developed as a portfolio project demonstrating Data Engineering, Data Analytics, and Business Intelligence skills.
