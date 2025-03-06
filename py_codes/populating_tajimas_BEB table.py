import pandas as pd
import sqlite3
import os

# ✅ Define Base Directory (move up one level to reach the root project folder)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DB_PATH = os.path.join(BASE_DIR, "instance", "db.db")  # ✅ Universal database path
CSV_PATH = os.path.join(BASE_DIR, "csv_files", "combined_TajimaD_sorted_BEB.csv")  # ✅ Universal CSV path

# ✅ Ensure CSV file exists
if not os.path.exists(CSV_PATH):
    raise FileNotFoundError(f"❌ CSV file not found: {CSV_PATH}")

# ✅ Load CSV file
df = pd.read_csv(CSV_PATH)

# ✅ Connect to SQLite database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# ✅ Loop through each row in the DataFrame and insert data into the tajimas_BEB table
for index, row in df.iterrows():
    # Extract relevant values from the row
    chrom = row['CHROM']
    bin_start = row['BIN_START']
    n_snps = row['N_SNPS']
    tajima_d = row['TajimaD']

    # ✅ Insert the row data into the tajimas_BEB table
    cursor.execute("""
        INSERT INTO tajimas_BEB (chromosome, bin_start, n_snps, tajimas_d)
        VALUES (?, ?, ?, ?);
    """, (chrom, bin_start, n_snps, tajima_d))

# ✅ Commit the changes to the database
conn.commit()

# ✅ Close the connection
cursor.close()
conn.close()

print(f"✅ TajimasD results successfully inserted into the tajimas_BEB table! Database: {DB_PATH}")

