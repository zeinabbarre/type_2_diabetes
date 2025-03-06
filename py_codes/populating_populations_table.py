import sqlite3
import pandas as pd
import os

# ✅ Define Base Directory (move up one level to reach the root project folder)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DB_PATH = os.path.join(BASE_DIR, "instance", "db.db")  # ✅ Universal database path
CSV_PATH = os.path.join(BASE_DIR, "csv_files", "final_population.csv")  # ✅ Universal CSV path

# ✅ Ensure CSV file exists
if not os.path.exists(CSV_PATH):
    raise FileNotFoundError(f"❌ CSV file not found: {CSV_PATH}")

# ✅ Load CSV file
df = pd.read_csv(CSV_PATH)

# ✅ Connect to SQLite database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# ✅ Ensure Populations table exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS Populations (
    pop_id INTEGER PRIMARY KEY AUTOINCREMENT,
    snp_id INTEGER NOT NULL,
    region TEXT NOT NULL,
    p_value REAL NOT NULL,
    sample_size TEXT,
    FOREIGN KEY (snp_id) REFERENCES SNPs(snp_id) ON DELETE CASCADE
);
""")

# ✅ Insert SNPs & Populations
for _, row in df.iterrows():
    snp_name = row["SNPS"]
    region = row["REGION"]
    p_value = row["P-VALUE"]  # No changes, always keeps the value
    sample_size = row["INITIAL SAMPLE SIZE"] if pd.notna(row["INITIAL SAMPLE SIZE"]) else None

    # ✅ Check if SNP already exists in SNPs table
    cursor.execute("SELECT snp_id FROM SNPs WHERE snp_name = ?", (snp_name,))
    result = cursor.fetchone()

    if result:
        snp_id = result[0]  # Existing SNP ID
    else:
        print(f"⚠️ SNP {snp_name} not found in SNPs table. Skipping...")
        continue  # Skip inserting population data if SNP doesn't exist

    # ✅ Insert Population Data
    cursor.execute("""
        INSERT INTO Populations (snp_id, region, p_value, sample_size)
        VALUES (?, ?, ?, ?)
    """, (snp_id, region, p_value, sample_size))

# ✅ Commit & close
conn.commit()
conn.close()

print(f"✅ Database successfully updated with Population data! Database: {DB_PATH}")

