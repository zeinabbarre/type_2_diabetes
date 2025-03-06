import sqlite3
import pandas as pd
import os

# ✅ Define Base Directory (moves up one level to reach the root project folder)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DB_PATH = os.path.join(BASE_DIR, "instance", "db.db")  # ✅ Universal database path
CSV_PATH = os.path.join(BASE_DIR, "csv_files", "fst_values_cleaned.csv")  # ✅ Universal CSV path

# ✅ Load the cleaned CSV
df = pd.read_csv(CSV_PATH)

# ✅ Connect to SQLite
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# ✅ Insert data while ensuring no NULL values are inserted
for index, row in df.iterrows():
    cursor.execute("""
        INSERT INTO Fst_Values (chromosome, position, fst_value, population_1, population_2)
        VALUES (?, ?, ?, ?, ?)
    """, (row["CHROM"], row["POS"], row["WEIR_AND_COCKERHAM_FST"], row["population_1"], row["population_2"]))

# ✅ Commit changes and close
conn.commit()
conn.close()

print("✅ Data inserted successfully!")
