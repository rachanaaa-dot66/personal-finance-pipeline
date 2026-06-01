import pandas as pd

# ── Category structure ───────────────────────────────────
# This is a clean reference / lookup table.
# No intentional messiness — it represents master data
# that the ETL will JOIN against to enrich transactions.

CATEGORIES = {
    "Food & Beverage": [
        "Rice & Noodles", "Street Food", "Coffee & Drinks",
        "Restaurant", "Supermarket", "Market / Psah", "Alcohol & Beer",
    ],
    "Transport": [
        "Tuk-Tuk", "PassApp / Grab", "Motorbike Fuel",
        "Bus / Van", "Car Rental", "Motodop", "Parking",
    ],
    "Housing": [
        "Rent", "Electricity (EDC)", "Water Bill",
        "Internet (Metfone/Cellcard)", "Home Maintenance", "Security Guard Fee",
    ],
    "Healthcare": [
        "Pharmacy", "Private Clinic", "Public Hospital",
        "Dental", "Traditional Medicine", "Health Insurance",
    ],
    "Education": [
        "School Fees", "University Tuition", "English Class",
        "Private Tutoring", "Stationery & Books", "Online Course",
    ],
    "Shopping": [
        "Clothing", "Electronics", "Aeon Mall",
        "Night Market", "Phone & Accessories", "Household Items",
    ],
    "Entertainment": [
        "Karaoke", "Cinema (Legend / Major)", "Gaming",
        "Streaming (Netflix/YouTube)", "Sports", "Tourism / Travel",
    ],
    "Telecommunications": [
        "Mobile Top-Up (Smart/Metfone)", "Data Package", "Roaming",
    ],
    "Religious & Social": [
        "Pagoda Donation", "Wedding Gift", "Funeral Contribution",
        "Bon Festival", "Community Fund",
    ],
    "Income": [
        "Monthly Salary", "Daily Wage", "Freelance / Gig Work",
        "Business Revenue", "Remittance (Received)",
        "Investment Return", "Government Allowance",
    ],
    "Savings & Transfer": [
        "Bank Deposit (ABA/ACLEDA)", "WING Money Transfer",
        "Family Support Sent", "Emergency Fund", "Gold Purchase",
    ],
}

# ── Spending type mapping ────────────────────────────────
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
    # Savings & Transfer
    "Bank Deposit (ABA/ACLEDA)": "Savings",
    "WING Money Transfer": "Savings",        # ✅ correct
    "Family Support Sent": "Essential",
    "Emergency Fund": "Savings",
    "Gold Purchase": "Savings",
}

# ── Build table ──────────────────────────────────────────
rows = []
for category, subcategories in CATEGORIES.items():
    for sub_category in subcategories:
        rows.append({
            "category":     category,
            "sub_category": sub_category,
            "spending_type": SUBCATEGORY_TYPE_MAP.get(sub_category, "Unknown"),
        })

df = pd.DataFrame(rows)
df = df.sort_values(["category", "sub_category"]).reset_index(drop=True)

# ── Save ─────────────────────────────────────────────────
import os
os.makedirs("data/processed", exist_ok=True)
df.to_csv("data/processed/categories.csv", index=False)

print("✅ categories.csv created")
print(f"   {len(df)} subcategories across {df['category'].nunique()} categories")
print(df.head())