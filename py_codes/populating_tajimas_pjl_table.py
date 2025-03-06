import sqlite3
import pandas as pd
import os

# ✅ Define Base Directory (move up one level to reach the root project folder)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DB_PATH = os.path.join(BASE_DIR, "instance", "db.db")  # ✅ Universal database path
CSV_PATH = os.path.join(BASE_DIR, "csv_files", "filtered_tajima_pjl.csv")  # ✅ Universal CSV path

# ✅ Ensure CSV file exists
if not os.path.exists(CSV_PATH):
    raise FileNotFoundError(f"❌ CSV file not found: {CSV_PATH}")

# ✅ Connect to SQLite
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# ✅ Load Tajima's D file
tajima_df = pd.read_csv(CSV_PATH)

# ✅ Ensure column names match the `tajimas_PJL` table
tajima_df.columns = ["chromosome", "bin_start", "n_snps", "tajimas_d"]  # Adjust if needed

# ✅ Option 1: Drop rows where 'tajimas_d' is NaN
# tajima_df = tajima_df.dropna(subset=["tajimas_d"])

# ✅ Option 2: Fill NaN values with 0 (or another default value)
tajima_df["tajimas_d"].fillna(0, inplace=True)  # Replace NaN with 0

# ✅ Save to SQLite
tajima_df.to_sql("tajimas_PJL", conn, if_exists="append", index=False)  # ✅ Append to existing table

print(f"✅ Tajima's D data imported successfully into tajimas_PJL! Database: {DB_PATH}")

# ✅ Close the connection
conn.close()
