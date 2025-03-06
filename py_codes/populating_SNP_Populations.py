import sqlite3
import csv
import os

# ✅ Define Base Directory (move up one level to reach the root project folder)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DB_PATH = os.path.join(BASE_DIR, "instance", "db.db")  # ✅ Universal database path
CSV_PATH = os.path.join(BASE_DIR, "csv_files", "final_population.csv")  # ✅ Universal CSV path

# ✅ Ensure CSV file exists
if not os.path.exists(CSV_PATH):
    raise FileNotFoundError(f"❌ CSV file not found: {CSV_PATH}")

# ✅ Connect to SQLite
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# ✅ Step 1: Build a dictionary of SNP name → snp_id (for fast lookups)
cursor.execute("SELECT snp_name, snp_id FROM SNPs")
snp_dict = {row[0]: row[1] for row in cursor.fetchall()}  # { "rs7018475": 1, "rs10761745": 2, ... }

# ✅ Step 2: Open the large CSV file and process it row by row
with open(CSV_PATH, "r", encoding="utf-8") as file:
    reader = csv.DictReader(file)  # Read CSV headers automatically

    to_insert = []  # Store batch insert values

    for row in reader:
        snp_name = row["SNPS"]
        sample_size = row["INITIAL SAMPLE SIZE"]
        p_value = float(row["P-VALUE"])
        region = row["REGION"]  # Directly using REGION as population

        # ✅ Look up snp_id from dictionary (fast lookup)
        snp_id = snp_dict.get(snp_name)

        if snp_id:  # Only insert if SNP exists in the database
            to_insert.append((snp_id, region, sample_size, p_value, region))

        # ✅ Insert in batches of 1000 rows to optimize performance
        if len(to_insert) >= 1000:
            cursor.executemany("""
                INSERT INTO SNP_Population (snp_id, population, sample_size, p_value, region)
                VALUES (?, ?, ?, ?, ?)
            """, to_insert)
            to_insert.clear()  # Empty batch after insert

# ✅ Final insert for remaining rows
if to_insert:
    cursor.executemany("""
        INSERT INTO SNP_Population (snp_id, population, sample_size, p_value, region)
        VALUES (?, ?, ?, ?, ?)
    """, to_insert)

# ✅ Commit changes and close connection
conn.commit()
conn.close()

print(f"✅ Data insertion complete! Database: {DB_PATH}")

