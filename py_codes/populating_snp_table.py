import pandas as pd
import sqlite3
import os

# ✅ Define Base Directory (move up one level to reach the root project folder)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DB_PATH = os.path.join(BASE_DIR, "instance", "db.db")  # ✅ Universal database path
CSV_PATH = os.path.join(BASE_DIR, "csv_files", "unique_snps.csv")  # ✅ Universal CSV path

# ✅ Ensure CSV file exists
if not os.path.exists(CSV_PATH):
    raise FileNotFoundError(f"❌ CSV file not found: {CSV_PATH}")

# ✅ Load CSV file into pandas DataFrame
df = pd.read_csv(CSV_PATH)

# ✅ Connect to SQLite database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# ✅ Insert SNP data into SNPs table
for index, row in df.iterrows():
    cursor.execute("""
        INSERT INTO SNPs (snp_name, chr_id, chr_pos)
        VALUES (?, ?, ?)
        ON CONFLICT(snp_name) DO NOTHING;  -- Avoid duplicates
    """, (row['snp_name'], row['chr_id'], row['chr_pos']))

# ✅ Commit changes and close connection
conn.commit()
cursor.close()
conn.close()

print(f"✅ SNP data successfully inserted into {DB_PATH}!")

