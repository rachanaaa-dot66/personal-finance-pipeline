import pandas as pd
import glob

files = glob.glob("data/raw/transactions_part_*.csv")

df = pd.concat(
    [pd.read_csv(file) for file in files],
    ignore_index=True
)

df.to_csv(
    "data/processed/transactions_raw_1M.csv",
    index=False
)

print("✅ Combined CSV created")
print(df.shape)