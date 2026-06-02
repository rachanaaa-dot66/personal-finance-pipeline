-- ─────────────────────────────────────────────────────────
-- Personal Finance Pipeline — PostgreSQL Init Script
-- Runs automatically when the postgres container first starts
-- Creates two databases: finance_db (data) + metabase_db (metabase internal)
-- ─────────────────────────────────────────────────────────

-- Metabase needs its own database to store its internal config
CREATE DATABASE metabase_db;

-- ── Connect to finance_db ─────────────────────────────
\c finance_db;

-- ── Dimension Table: customers ────────────────────────
CREATE TABLE IF NOT EXISTS customers (
    customer_id         VARCHAR(10),
    name                VARCHAR(100),
    age                 INT,
    gender              VARCHAR(10),
    marital_status      VARCHAR(10),
    city                VARCHAR(50),
    income_level        VARCHAR(20),
    monthly_income_usd  NUMERIC(10, 2),
    occupation          VARCHAR(50),
    account_type        VARCHAR(20),
    customer_since      DATE
);

-- ── Dimension Table: categories ───────────────────────
CREATE TABLE IF NOT EXISTS categories (
    sub_category    VARCHAR(100),
    category        VARCHAR(50),
    spending_type   VARCHAR(20)
);

-- ── Fact Table: transactions_cleaned ─────────────────
-- No FK constraints — Spark writes in parallel partitions,
-- FK checks cause race conditions. Data integrity enforced in ETL instead.
CREATE TABLE IF NOT EXISTS transactions_cleaned (
    transaction_id      VARCHAR(36),
    customer_id         VARCHAR(10),
    date                DATE,
    amount              NUMERIC(15, 2),
    currency            VARCHAR(20),
    amount_usd          NUMERIC(15, 2),
    category            VARCHAR(50),
    sub_category        VARCHAR(100),
    spending_type       VARCHAR(20),
    transaction_type    VARCHAR(20),
    payment_method      VARCHAR(50),
    notes               TEXT,
    is_anomaly          BOOLEAN         DEFAULT FALSE
);

-- ── Indexes for dashboard query performance ───────────
CREATE INDEX IF NOT EXISTS idx_tx_customer   ON transactions_cleaned(customer_id);
CREATE INDEX IF NOT EXISTS idx_tx_date       ON transactions_cleaned(date);
CREATE INDEX IF NOT EXISTS idx_tx_category   ON transactions_cleaned(category);
CREATE INDEX IF NOT EXISTS idx_tx_type       ON transactions_cleaned(spending_type);