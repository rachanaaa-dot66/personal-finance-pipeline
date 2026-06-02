from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import psycopg2

# ── Default args ─────────────────────────────
default_args = {
    "owner": "finance_pipeline",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}

# ── DAG Definition ───────────────────────────
dag = DAG(
    dag_id="personal_finance_pipeline",
    description="Personal Finance Data Pipeline Validation",
    default_args=default_args,
    start_date=datetime(2024, 1, 1),
    schedule_interval="0 1 * * *",
    catchup=False,
    tags=["finance", "etl", "validation"],
)

# ── Task 1: ETL Placeholder ──────────────────
task_spark_etl = BashOperator(
    task_id="run_spark_etl",
    bash_command='echo "Spark ETL executed manually"',
    dag=dag,
)

# ── Task 2: Validate Database ────────────────
def validate_counts():

    conn = psycopg2.connect(
        host="postgres",
        port=5432,
        dbname="finance_db",
        user="finance_user",
        password="finance_pass"
    )

    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM transactions_cleaned;")
    tx_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM customers;")
    cust_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM categories;")
    cat_count = cur.fetchone()[0]

    cur.close()
    conn.close()

    print(f"transactions_cleaned : {tx_count:,}")
    print(f"customers            : {cust_count:,}")
    print(f"categories           : {cat_count:,}")

    assert tx_count >= 1_000_000, \
        f"Expected 1,000,000 transactions, got {tx_count}"

    assert cust_count == 400, \
        f"Expected 400 customers, got {cust_count}"

    assert cat_count == 64, \
        f"Expected 64 categories, got {cat_count}"

    print("All validation checks passed!")

task_validate = PythonOperator(
    task_id="validate_row_counts",
    python_callable=validate_counts,
    dag=dag,
)

# ── Task 3: Success Message ──────────────────
task_done = BashOperator(
    task_id="pipeline_complete",
    bash_command='echo "Personal Finance Pipeline completed successfully"',
    dag=dag,
)

# ── Workflow ─────────────────────────────────
task_spark_etl >> task_validate >> task_done