from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import DoubleType, DateType
import re

# ── Spark Session ─────────────────────────────────────────
spark = SparkSession.builder \
    .appName("PersonalFinanceETL") \
    .config("spark.jars.packages", "org.postgresql:postgresql:42.6.0") \
    .config("spark.sql.legacy.timeParserPolicy", "LEGACY") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

print("=" * 60)
print("  Personal Finance Pipeline — Spark ETL")
print("=" * 60)

# ── Paths ─────────────────────────────────────────────────
TRANSACTIONS_PATH = "/opt/spark/data/processed/transactions_raw_1M.csv"
CUSTOMERS_PATH    = "/opt/spark/data/processed/customers.csv"
CATEGORIES_PATH   = "/opt/spark/data/processed/categories.csv"
OUTPUT_PATH       = "/opt/spark/data/processed/transactions_cleaned"

PG_URL  = "jdbc:postgresql://postgres:5432/finance_db"
PG_PROPS = {
    "user":     "finance_user",
    "password": "finance_pass",
    "driver":   "org.postgresql.Driver"
}

# ═══════════════════════════════════════════════════════════
# STEP 1 — Load raw data
# ═══════════════════════════════════════════════════════════
print("\n[1/6] Loading raw data...")

tx   = spark.read.option("header", True).option("inferSchema", False).csv(TRANSACTIONS_PATH)
cats = spark.read.option("header", True).csv(CATEGORIES_PATH)
custs = spark.read.option("header", True).csv(CUSTOMERS_PATH)

raw_count = tx.count()
print(f"      Transactions loaded : {raw_count:,}")
print(f"      Customers loaded    : {custs.count():,}")
print(f"      Categories loaded   : {cats.count():,}")

# ═══════════════════════════════════════════════════════════
# STEP 2 — Remove duplicates
# ═══════════════════════════════════════════════════════════
print("\n[2/6] Removing duplicates...")

tx = tx.dropDuplicates(["transaction_id"])
dedup_count = tx.count()
print(f"      Removed  : {raw_count - dedup_count:,} duplicate rows")
print(f"      Remaining: {dedup_count:,}")

# ═══════════════════════════════════════════════════════════
# STEP 3 — Clean text columns
# ═══════════════════════════════════════════════════════════
print("\n[3/6] Cleaning text columns...")

# Trim whitespace + title-case for category fields and payment_method
tx = tx \
    .withColumn("category",         F.initcap(F.trim(F.col("category")))) \
    .withColumn("sub_category",     F.lower(F.trim(F.col("sub_category")))) \
    .withColumn("transaction_type", F.lower(F.trim(F.col("transaction_type")))) \
    .withColumn("payment_method",   F.initcap(F.trim(F.col("payment_method")))) \
    .withColumn("currency",         F.upper(F.trim(F.col("currency"))))

# Standardise city variants in customers (lowercase → title case)
custs = custs \
    .withColumn("city", F.initcap(F.trim(F.col("city")))) \
    .withColumn("name", F.initcap(F.trim(F.col("name"))))

# Fix known city alternate spellings → canonical name
city_map = {
    "Phnompenh":      "Phnom Penh",
    "Phnom-Penh":     "Phnom Penh",
    "Siemreap":       "Siem Reap",
    "Batdambang":     "Battambang",
    "Kampong Saom":   "Sihanoukville",
    "Sihanoukvile":   "Sihanoukville",
    "Kompong Cham":   "Kampong Cham",
    "Kratié":         "Kratie",
    "Kompong Speu":   "Kampong Speu",
    "Preyveng":       "Prey Veng",
    "Svayrieng":      "Svay Rieng",
}
for dirty, clean in city_map.items():
    custs = custs.withColumn(
        "city",
        F.when(F.col("city") == dirty, clean).otherwise(F.col("city"))
    )

print("      Text columns standardised")

# ═══════════════════════════════════════════════════════════
# STEP 4 — Fix dates (mixed formats → standard DATE)
# ═══════════════════════════════════════════════════════════
print("\n[4/6] Standardising dates...")

# Three formats present: YYYY-MM-DD / DD/MM/YYYY / MM-DD-YYYY
tx = tx.withColumn(
    "date_clean",
    F.coalesce(
        F.to_date(F.col("date"), "yyyy-MM-dd"),    # ISO  — most common
        F.to_date(F.col("date"), "dd/MM/yyyy"),    # DD/MM/YYYY
        F.to_date(F.col("date"), "MM-dd-yyyy"),    # MM-DD-YYYY
    )
).drop("date").withColumnRenamed("date_clean", "date")

bad_dates = tx.filter(F.col("date").isNull()).count()
print(f"      Unparseable dates dropped: {bad_dates:,}")
tx = tx.filter(F.col("date").isNotNull())

# ═══════════════════════════════════════════════════════════
# STEP 5 — Fix & validate amounts
# ═══════════════════════════════════════════════════════════
print("\n[5/6] Cleaning amounts...")

KHR_TO_USD = 1 / 4100

# amount may be a string like "1,250.00" — strip commas then cast
tx = tx.withColumn(
    "amount",
    F.regexp_replace(F.col("amount").cast("string"), ",", "").cast(DoubleType())
).withColumn(
    "amount_usd",
    F.col("amount_usd").cast(DoubleType())
)

# Flag anomalies: negative or zero amount
tx = tx.withColumn(
    "is_anomaly",
    F.when(
        (F.col("amount") <= 0) | (F.col("amount").isNull()),
        True
    ).otherwise(False)
)

anomaly_count = tx.filter(F.col("is_anomaly") == True).count()
print(f"      Anomalous amounts flagged: {anomaly_count:,} (kept with is_anomaly=true)")

# Recalculate missing amount_usd from amount + currency
tx = tx.withColumn(
    "amount_usd",
    F.when(
        F.col("amount_usd").isNull() & (F.col("currency") == "KHR"),
        F.round(F.col("amount") * KHR_TO_USD, 2)
    ).when(
        F.col("amount_usd").isNull() & (F.col("currency") == "USD"),
        F.col("amount")
    ).otherwise(F.col("amount_usd"))
)

# ═══════════════════════════════════════════════════════════
# STEP 6 — Handle nulls
# ═══════════════════════════════════════════════════════════
print("\n[6/6] Handling nulls...")

tx = tx \
    .fillna({"currency":         "Unknown"}) \
    .fillna({"payment_method":   "Unknown"}) \
    .fillna({"transaction_type": "Unknown"}) \
    .fillna({"sub_category":     "Uncategorised"}) \
    .fillna({"notes":            ""})

# Fix customers: age outliers → null, income anomalies → null
custs = custs \
    .withColumn("age",
        F.when((F.col("age").cast("int") < 15) | (F.col("age").cast("int") > 90), None)
        .otherwise(F.col("age").cast("int"))
    ) \
    .withColumn("monthly_income_usd",
        F.when(F.col("monthly_income_usd").cast("double") <= 0, None)
        .otherwise(F.col("monthly_income_usd").cast("double"))
    )

print("      Nulls filled / anomalies nulled in customers")

# ═══════════════════════════════════════════════════════════
# JOIN — Enrich transactions with categories
# ═══════════════════════════════════════════════════════════
print("\nJoining with categories to re-derive spending_type...")

# Drop the raw spending_type (may be null/dirty) and re-derive from categories table
cats_clean = cats.select(
    F.lower(F.trim(F.col("sub_category"))).alias("sub_category"),
    F.col("spending_type").alias("spending_type_clean"),
    F.initcap(F.trim(F.col("category"))).alias("category_clean"),
)

tx = tx.drop("spending_type") \
    .join(cats_clean, on="sub_category", how="left") \
    .withColumnRenamed("spending_type_clean", "spending_type") \
    .withColumn("spending_type", F.coalesce(F.col("spending_type"), F.lit("Unknown")))

# ═══════════════════════════════════════════════════════════
# Final column selection & ordering
# ═══════════════════════════════════════════════════════════
tx_final = tx.select(
    "transaction_id",
    "customer_id",
    "date",
    "amount",
    "currency",
    "amount_usd",
    "category",
    "sub_category",
    "spending_type",
    "transaction_type",
    "payment_method",
    "notes",
    "is_anomaly",
)

final_count = tx_final.count()
print(f"\n{'=' * 60}")
print(f"  ETL complete — {final_count:,} clean rows")
print(f"  Removed {raw_count - final_count:,} rows total (dupes + bad dates)")
print(f"{'=' * 60}")

# ═══════════════════════════════════════════════════════════
# WRITE — CSV output
# ═══════════════════════════════════════════════════════════
print("\nWriting transactions_cleaned.csv...")
tx_final.coalesce(1).write.mode("overwrite") \
    .option("header", True) \
    .csv(OUTPUT_PATH)
print("  Saved to data/processed/transactions_cleaned.csv")

# ═══════════════════════════════════════════════════════════
# WRITE — PostgreSQL (fact + dimension tables)
# ═══════════════════════════════════════════════════════════
print("\nLoading to PostgreSQL...")

# Tables are truncated before this script runs via:
# docker exec postgres psql -U finance_user -d finance_db -c "TRUNCATE TABLE transactions_cleaned CASCADE; TRUNCATE TABLE customers CASCADE; TRUNCATE TABLE categories CASCADE;"
print("  Writing to PostgreSQL (append mode)...")

# Load dimensions first, then fact (FK order)
cats.write.jdbc(url=PG_URL, table="categories",
    mode="append", properties=PG_PROPS)
print("  categories loaded")

# Cast date/numeric columns to correct types before writing to PostgreSQL
custs = custs     .withColumn("customer_since",       F.to_date(F.col("customer_since"), "yyyy-MM-dd"))     .withColumn("monthly_income_usd",   F.col("monthly_income_usd").cast("double"))     .withColumn("age",                  F.col("age").cast("int"))

custs.write.jdbc(url=PG_URL, table="customers",
    mode="append", properties=PG_PROPS)
print("  customers loaded")

tx_final.write.jdbc(url=PG_URL, table="transactions_cleaned",
    mode="append", properties=PG_PROPS)
print("  transactions_cleaned loaded")

print(f"\nAll done! Check Metabase at http://localhost:3000")
spark.stop()