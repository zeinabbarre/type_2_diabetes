import sqlite3
import pandas as pd

# Connect to SQLite
db_path = "/mnt/c/Users/Hp EliteBook 840 G3/OneDrive/Desktop/type_2_diabetes/instance/db.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Load Tajima's D file
tajima_df = pd.read_csv("/mnt/c/Users/Hp EliteBook 840 G3/OneDrive/Desktop/type_2_diabetes/csv_files/filtered_tajima_pjl.csv")

# Ensure column names match the `tajimas_PJL` table
tajima_df.columns = ["chromosome", "bin_start", "n_snps", "tajimas_d"]  # Adjust if needed

# Option 1: Drop rows where 'tajimas_d' is NaN
# tajima_df = tajima_df.dropna(subset=["tajimas_d"])

# Option 2: Fill NaN values with 0 (or another default value)
tajima_df["tajimas_d"].fillna(0, inplace=True)  # Replace NaN with 0

# Save to SQLite
tajima_df.to_sql("tajimas_PJL", conn, if_exists="append", index=False)  # ✅ Append to existing table

print("✅ Tajima's D data imported successfully into tajimas_PJL!")
conn.close()

