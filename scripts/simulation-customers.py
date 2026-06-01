import os
import pandas as pd
import random
import numpy as np
from faker import Faker

fake = Faker()
random.seed(42)
np.random.seed(42)

# ── Config ───────────────────────────────────────────────
NUM_CUSTOMERS = 400

# ── Cambodian Cities ─────────────────────────────────────
# Clean canonical names (reference dimension table)
CITIES = [
    "Phnom Penh", "Siem Reap", "Battambang", "Sihanoukville",
    "Kampot", "Kampong Cham", "Kratie", "Takeo",
    "Kampong Speu", "Pursat", "Prey Veng", "Svay Rieng"
]
CITY_WEIGHTS = [0.40, 0.18, 0.10, 0.08, 0.05, 0.05,
                0.03, 0.03, 0.02, 0.02, 0.02, 0.02]

# ── City name variants (simulates manual data entry / multiple source systems) ──
CITY_VARIANTS = {
    "Phnom Penh":    ["Phnom Penh", "phnom penh", "PHNOM PENH", "PhnomPenh", "Phnom-Penh"],
    "Siem Reap":     ["Siem Reap",  "siem reap",  "SIEM REAP",  "SiemReap"],
    "Battambang":    ["Battambang", "battambang", "Batdambang"],
    "Sihanoukville": ["Sihanoukville", "sihanoukville", "Sihanoukvile", "Kampong Saom"],
    "Kampot":        ["Kampot",     "kampot",     "KAMPOT"],
    "Kampong Cham":  ["Kampong Cham", "Kompong Cham", "kampong cham"],
    "Kratie":        ["Kratie",     "kratie",     "Kratié"],
    "Takeo":         ["Takeo",      "takeo",      "TAKEO"],
    "Kampong Speu":  ["Kampong Speu", "Kompong Speu"],
    "Pursat":        ["Pursat",     "pursat"],
    "Prey Veng":     ["Prey Veng",  "prey veng",  "PreyVeng"],
    "Svay Rieng":    ["Svay Rieng", "svay rieng", "SvayRieng"],
}

# ── Income Levels (Monthly USD) ──────────────────────────
INCOME_LEVELS = {
    "Low":          (120,  300),
    "Lower-Middle": (300,  600),
    "Middle":       (600,  1200),
    "Upper-Middle": (1200, 2500),
    "High":         (2500, 6000),
}
INCOME_WEIGHTS = [0.30, 0.30, 0.22, 0.12, 0.06]

# ── Khmer Names ──────────────────────────────────────────
KHMER_FIRST = [
    "Sokha", "Dara", "Chanthy", "Virak", "Sreymom",
    "Piseth", "Bopha", "Rathana", "Kimly", "Sovann",
    "Molika", "Vanna", "Chenda", "Rithy", "Sophea",
    "Mengly", "Kosal", "Nita", "Bunna", "Theary",
    "Sothea", "Chamroeun", "Lida", "Vuthy"
]
KHMER_LAST = [
    "Chan", "Sok", "Keo", "Ly", "Pov", "Heng",
    "Nget", "Tep", "Oum", "Chhun", "Mao",
    "Lim", "Sar", "Touch", "Im", "Ros"
]

# ── Occupation Mapping (by income level) ─────────────────
OCCUPATION_MAPPING = {
    "Low":          ["Garment Worker", "Farmer", "Construction Worker",
                     "Driver", "Street Vendor"],
    "Lower-Middle": ["Trader", "Civil Servant", "Teacher", "Retail Staff"],
    "Middle":       ["Teacher", "NGO Staff", "Healthcare Worker", "Accountant"],
    "Upper-Middle": ["IT Professional", "Business Owner", "Bank Employee", "Engineer"],
    "High":         ["Business Owner", "Senior Executive", "Investor", "Company Director"],
}

ACCOUNT_TYPES   = ["Savings", "Current", "Mobile Wallet"]
ACCOUNT_WEIGHTS = [0.60, 0.15, 0.25]

# ── Messiness helpers ────────────────────────────────────
def maybe_null(val, prob=0.03):
    return None if random.random() < prob else val

def messy_city(canonical_city):
    """Return a random variant of the city name (~30% chance of dirty variant)."""
    variants = CITY_VARIANTS.get(canonical_city, [canonical_city])
    if random.random() < 0.30:
        return random.choice(variants)   # could be dirty
    return canonical_city                # clean canonical

# ── Generate customers ───────────────────────────────────
income_keys   = list(INCOME_LEVELS.keys())
chosen_levels = random.choices(income_keys, weights=INCOME_WEIGHTS, k=NUM_CUSTOMERS)

customers = []

for i in range(1, NUM_CUSTOMERS + 1):
    level              = chosen_levels[i - 1]
    low_income, high_income = INCOME_LEVELS[level]
    canonical_city     = random.choices(CITIES, weights=CITY_WEIGHTS)[0]

    # Age: mostly 18–65, but inject a few outliers (~1%)
    if random.random() < 0.01:
        age = random.choice([0, 999, 150])   # bad data
    else:
        age = random.randint(18, 65)

    # Monthly income: mostly realistic, ~1.5% have anomalies
    if random.random() < 0.015:
        monthly_income = random.choice([-500.0, 0.0, None])
    else:
        monthly_income = round(random.uniform(low_income, high_income), 2)

    customer = {
        "customer_id":        f"CUST_{i:04d}",

        # Name — clean (names don't usually have casing issues in a banking system)
        "name": (
            f"{random.choice(KHMER_FIRST)} "
            f"{random.choice(KHMER_LAST)}"
        ),

        # Age — mostly valid, ~1% outlier
        "age":              age,

        "gender":           random.choice(["Male", "Female"]),

        "marital_status":   random.choice(["Single", "Married"]),

        # City — ~30% dirty variant (casing / alternate spelling)
        "city":             messy_city(canonical_city),

        "income_level":     level,

        # Monthly income — mostly valid, ~1.5% anomaly
        "monthly_income_usd": monthly_income,

        "occupation":       random.choice(OCCUPATION_MAPPING[level]),

        "account_type":     random.choices(ACCOUNT_TYPES, weights=ACCOUNT_WEIGHTS)[0],

        "customer_since":   fake.date_between(
                                start_date="-8y",
                                end_date="-30d"
                            ).isoformat(),
    }
    customers.append(customer)

# ── Create DataFrame ─────────────────────────────────────
df = pd.DataFrame(customers)
df = df.sort_values("customer_id").reset_index(drop=True)

# ── Save ─────────────────────────────────────────────────
os.makedirs("data/processed", exist_ok=True)
df.to_csv("data/processed/customers.csv", index=False)

print("✅ customers.csv created")
print(f"   {len(df)} customers")
print(f"\n   Intentional messiness injected:")
print(f"   • City name variants (~30%): casing, alternate spellings")
print(f"   • Age outliers (~1%): 0, 999, 150")
print(f"   • monthly_income_usd anomalies (~1.5%): negative, zero, null")
print(df.head())