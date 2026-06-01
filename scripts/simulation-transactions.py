import pandas as pd
import numpy as np
from faker import Faker
import random
import os
from tqdm import tqdm

fake = Faker()
random.seed(42)
np.random.seed(42)

# ── Config ───────────────────────────────────────────────
TOTAL_ROWS    = 1_000_000
CHUNK_SIZE    = 100_000
OUTPUT_DIR    = "data/raw"
NUM_CUSTOMERS = 400

# ── Cambodia Dual-Currency Economy ───────────────────────
CURRENCIES      = ["KHR", "USD"]
CURRENCY_WEIGHT = [0.55, 0.45]
KHR_TO_USD      = 1 / 4100

# ── Cambodian Cities ─────────────────────────────────────
CITIES = [
    "Phnom Penh", "Siem Reap", "Battambang", "Sihanoukville",
    "Kampot", "Kampong Cham", "Kratie", "Takeo",
    "Kampong Speu", "Pursat", "Prey Veng", "Svay Rieng"
]
CITY_WEIGHTS = [0.40, 0.18, 0.10, 0.08, 0.05, 0.05,
                0.03, 0.03, 0.02, 0.02, 0.02, 0.02]

# ── Categories ───────────────────────────────────────────
CATEGORIES = {
    "Food & Beverage": {
        "sub_categories": ["Rice & Noodles", "Street Food", "Coffee & Drinks",
                           "Restaurant", "Supermarket", "Market / Psah", "Alcohol & Beer"],
        "amount_range_khr": (2_000, 80_000),
        "transaction_type": "debit",
    },
    "Transport": {
        "sub_categories": ["Tuk-Tuk", "PassApp / Grab", "Motorbike Fuel",
                           "Bus / Van", "Car Rental", "Motodop", "Parking"],
        "amount_range_khr": (4_000, 200_000),
        "transaction_type": "debit",
    },
    "Housing": {
        "sub_categories": ["Rent", "Electricity (EDC)", "Water Bill",
                           "Internet (Metfone/Cellcard)", "Home Maintenance", "Security Guard Fee"],
        "amount_range_khr": (100_000, 2_000_000),
        "transaction_type": "debit",
    },
    "Healthcare": {
        "sub_categories": ["Pharmacy", "Private Clinic", "Public Hospital",
                           "Dental", "Traditional Medicine", "Health Insurance"],
        "amount_range_khr": (10_000, 800_000),
        "transaction_type": "debit",
    },
    "Education": {
        "sub_categories": ["School Fees", "University Tuition", "English Class",
                           "Private Tutoring", "Stationery & Books", "Online Course"],
        "amount_range_khr": (20_000, 1_200_000),
        "transaction_type": "debit",
    },
    "Shopping": {
        "sub_categories": ["Clothing", "Electronics", "Aeon Mall",
                           "Night Market", "Phone & Accessories", "Household Items"],
        "amount_range_khr": (20_000, 1_600_000),
        "transaction_type": "debit",
    },
    "Entertainment": {
        "sub_categories": ["Karaoke", "Cinema (Legend / Major)", "Gaming",
                           "Streaming (Netflix/YouTube)", "Sports", "Tourism / Travel"],
        "amount_range_khr": (8_000, 400_000),
        "transaction_type": "debit",
    },
    "Telecommunications": {
        "sub_categories": ["Mobile Top-Up (Smart/Metfone)", "Data Package", "Roaming"],
        "amount_range_khr": (4_000, 80_000),
        "transaction_type": "debit",
    },
    "Religious & Social": {
        "sub_categories": ["Pagoda Donation", "Wedding Gift", "Funeral Contribution",
                           "Bon Festival", "Community Fund"],
        "amount_range_khr": (10_000, 400_000),
        "transaction_type": "debit",
    },
    "Income": {
        "sub_categories": ["Monthly Salary", "Daily Wage", "Freelance / Gig Work",
                           "Business Revenue", "Remittance (Received)",
                           "Investment Return", "Government Allowance"],
        "amount_range_khr": (500_000, 12_000_000),
        "transaction_type": "credit",
    },
    "Savings & Transfer": {
        "sub_categories": ["Bank Deposit (ABA/ACLEDA)", "WING Money Transfer",
                           "Family Support Sent", "Emergency Fund", "Gold Purchase"],
        "amount_range_khr": (40_000, 4_000_000),
        "transaction_type": "debit",
    },
}

SUBCATEGORY_TYPE_MAP = {
    # Food & Beverage
    "Rice & Noodles": "Essential",      "Street Food": "Essential",
    "Coffee & Drinks": "Non-Essential", "Restaurant": "Non-Essential",
    "Supermarket": "Essential",         "Market / Psah": "Essential",
    "Alcohol & Beer": "Non-Essential",
    # Transport
    "Tuk-Tuk": "Essential",            "PassApp / Grab": "Essential",
    "Motorbike Fuel": "Essential",      "Bus / Van": "Essential",
    "Car Rental": "Non-Essential",      "Motodop": "Essential",
    "Parking": "Non-Essential",
    # Housing
    "Rent": "Essential",                "Electricity (EDC)": "Essential",
    "Water Bill": "Essential",          "Internet (Metfone/Cellcard)": "Essential",
    "Home Maintenance": "Essential",    "Security Guard Fee": "Essential",
    # Healthcare
    "Pharmacy": "Essential",            "Private Clinic": "Essential",
    "Public Hospital": "Essential",     "Dental": "Essential",
    "Traditional Medicine": "Non-Essential", "Health Insurance": "Essential",
    # Education
    "School Fees": "Essential",         "University Tuition": "Essential",
    "English Class": "Essential",       "Private Tutoring": "Essential",
    "Stationery & Books": "Essential",  "Online Course": "Non-Essential",
    # Shopping
    "Clothing": "Non-Essential",        "Electronics": "Non-Essential",
    "Aeon Mall": "Non-Essential",       "Night Market": "Non-Essential",
    "Phone & Accessories": "Non-Essential", "Household Items": "Essential",
    # Entertainment
    "Karaoke": "Non-Essential",         "Cinema (Legend / Major)": "Non-Essential",
    "Gaming": "Non-Essential",          "Streaming (Netflix/YouTube)": "Non-Essential",
    "Sports": "Non-Essential",          "Tourism / Travel": "Non-Essential",
    # Telecommunications
    "Mobile Top-Up (Smart/Metfone)": "Essential",
    "Data Package": "Essential",        "Roaming": "Non-Essential",
    # Religious & Social
    "Pagoda Donation": "Non-Essential", "Wedding Gift": "Non-Essential",
    "Funeral Contribution": "Essential","Bon Festival": "Non-Essential",
    "Community Fund": "Non-Essential",
    # Income
    "Monthly Salary": "Income",         "Daily Wage": "Income",
    "Freelance / Gig Work": "Income",   "Business Revenue": "Income",
    "Remittance (Received)": "Income",  "Investment Return": "Income",
    "Government Allowance": "Income",
    # Savings & Transfer  ← WING Money Transfer fixed to Savings
    "Bank Deposit (ABA/ACLEDA)": "Savings",
    "WING Money Transfer": "Savings",        # ✅ fixed (was Non-Essential)
    "Family Support Sent": "Essential",
    "Emergency Fund": "Savings",
    "Gold Purchase": "Savings",
}

PAYMENT_METHODS = [
    "Cash (KHR)", "Cash (USD)", "ABA Bank", "ACLEDA Bank",
    "WING", "Pi Pay", "TrueMoney", "Bakong", "Metfone e-Money", "Bank Transfer",
]
PAYMENT_WEIGHTS = [0.20, 0.18, 0.22, 0.12, 0.10,
                   0.05, 0.05, 0.04, 0.02, 0.02]

# ── Date format variants (simulates exports from different systems) ──
DATE_FORMATS = ["iso", "dmy_slash", "mdy_dash", "iso"]   # iso weighted 2x
def messy_date(d):
    """Return date string in a randomly chosen format."""
    fmt = random.choice(DATE_FORMATS)
    if fmt == "iso":
        return d.isoformat()                          # 2024-03-15
    elif fmt == "dmy_slash":
        return d.strftime("%d/%m/%Y")                 # 15/03/2024
    elif fmt == "mdy_dash":
        return d.strftime("%m-%d-%Y")                 # 03-15-2024
    return d.isoformat()

# ── Messiness helpers ────────────────────────────────────
def messy_text(val, prob_lower=0.10, prob_upper=0.07, prob_space=0.05):
    """Random casing + trailing/leading whitespace."""
    r = random.random()
    if r < prob_lower:
        return val.lower()
    if r < prob_lower + prob_upper:
        return val.upper()
    if r < prob_lower + prob_upper + prob_space:
        return "  " + val + "  "
    return val

def messy_amount(val):
    """
    ~6% chance of formatting the amount as a string with commas
    (simulates Excel or legacy system exports).
    ~2% chance of being negative (data entry error).
    ~1% chance of being 0.
    """
    r = random.random()
    if r < 0.01:
        return 0                                      # zero amount
    if r < 0.03:
        return -abs(val)                              # negative amount
    if r < 0.09:
        return f"{val:,.2f}"                          # "1,250.00" string
    return round(val, 2)

def maybe_null(val, prob=0.04):
    return None if random.random() < prob else val

# ── Chunk generator ──────────────────────────────────────
def generate_chunk(size):
    records   = []
    cat_names = list(CATEGORIES.keys())

    for _ in range(size):
        cat_name  = random.choice(cat_names)
        cat_data  = CATEGORIES[cat_name]
        sub_cat   = random.choice(cat_data["sub_categories"])
        tx_type   = cat_data["transaction_type"]
        spending_type = SUBCATEGORY_TYPE_MAP.get(sub_cat, "Unknown")

        # Currency
        if cat_name == "Income":
            currency = random.choices(["USD", "KHR"], weights=[0.60, 0.40])[0]
        else:
            currency = random.choices(CURRENCIES, weights=CURRENCY_WEIGHT)[0]

        # Amount
        lo, hi     = cat_data["amount_range_khr"]
        amount_khr = round(random.uniform(lo, hi), 0)

        if currency == "KHR":
            amount     = amount_khr
            amount_usd = round(amount_khr * KHR_TO_USD, 2)
        else:
            amount_usd = round(amount_khr * KHR_TO_USD, 2)
            amount     = amount_usd

        # Introduce wrong/missing amount_usd (~4% of rows)
        if random.random() < 0.04:
            amount_usd = None

        raw_date = fake.date_between(start_date="-3y", end_date="today")

        record = {
            "transaction_id":   fake.uuid4(),
            "customer_id":      f"CUST_{random.randint(1, NUM_CUSTOMERS):04d}",

            # Messy dates — mixed formats (~25% non-ISO)
            "date":             messy_date(raw_date),

            # Messy amounts — strings, zeros, negatives
            "amount":           maybe_null(messy_amount(round(amount, 2)), prob=0.03),

            # Currency missing ~3%
            "currency":         maybe_null(currency, prob=0.03),

            # amount_usd missing ~4% (set above)
            "amount_usd":       amount_usd,

            # Category: messy casing + missing ~4%
            "category":         messy_text(maybe_null(cat_name, prob=0.04) or cat_name),

            # Sub-category: messy casing + missing ~6%
            "sub_category":     maybe_null(messy_text(sub_cat), prob=0.06),

            # spending_type: missing ~3% (derived, ETL should re-derive)
            "spending_type":    maybe_null(spending_type, prob=0.03),

            # transaction_type: messy casing + missing ~3%
            "transaction_type": maybe_null(messy_text(tx_type), prob=0.03),

            # payment_method: missing ~6%
            "payment_method":   maybe_null(
                                    messy_text(
                                        random.choices(PAYMENT_METHODS,
                                                       weights=PAYMENT_WEIGHTS)[0]
                                    ),
                                    prob=0.06
                                ),

            # notes: free-text field, missing ~45%
            "notes":            maybe_null(
                                    random.choice([
                                        "ok", "done", "paid", "received",
                                        "monthly payment", "urgent", "",
                                        "check later", "ref#" + str(random.randint(1000, 9999))
                                    ]),
                                    prob=0.45
                                ),
        }
        records.append(record)

    df = pd.DataFrame(records)

    # Inject ~3% duplicate rows (simulates double-submission / retry)
    dup_count  = int(len(df) * 0.03)
    duplicates = df.sample(n=dup_count, replace=True)
    df = pd.concat([df, duplicates], ignore_index=True)
    return df

# ── Main ─────────────────────────────────────────────────
def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    chunks = TOTAL_ROWS // CHUNK_SIZE
    print(f"🇰🇭 Generating {TOTAL_ROWS:,} transactions in {chunks} chunks...\n")

    for i in tqdm(range(chunks), desc="Generating"):
        df   = generate_chunk(CHUNK_SIZE)
        path = os.path.join(OUTPUT_DIR, f"transactions_part_{i+1:02d}.csv")
        df.to_csv(path, index=False)

    print("\n✅ Done!")
    print(f"   • {chunks} transaction chunk CSVs → {OUTPUT_DIR}/")
    print(f"\n   Intentional messiness injected:")
    print(f"   • Mixed date formats (ISO / DD/MM/YYYY / MM-DD-YYYY)")
    print(f"   • Amount as comma-formatted string (~6%), negatives (~2%), zeros (~1%)")
    print(f"   • Nulls: amount ~3%, currency ~3%, amount_usd ~4%,")
    print(f"            sub_category ~6%, payment_method ~6%, notes ~45%")
    print(f"   • Casing noise on category, sub_category, transaction_type, payment_method")
    print(f"   • ~3% duplicate rows (double-submission simulation)")

if __name__ == "__main__":
    main()