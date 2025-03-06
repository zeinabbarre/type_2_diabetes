import pandas as pd
import sqlite3
import os

# ✅ Define Base Directory (move up one level to reach the root project folder)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DB_PATH = os.path.join(BASE_DIR, "instance", "db.db")  # ✅ Universal database path
CSV_PATH = os.path.join(BASE_DIR, "csv_files", "unique_mapped_genes.csv")  # ✅ Universal CSV path

# ✅ Ensure CSV file exists
if not os.path.exists(CSV_PATH):
    raise FileNotFoundError(f"❌ CSV file not found: {CSV_PATH}")

# ✅ Load CSV file
df = pd.read_csv(CSV_PATH)

# ✅ Remove duplicates (ensures unique genes)
df = df.drop_duplicates(subset=['gene_name'])

# ✅ Connect to SQLite database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# ✅ Insert data into Genes table
for index, row in df.iterrows():
    cursor.execute("""
        INSERT INTO Genes (gene_name)
        VALUES (?)
        ON CONFLICT(gene_name) DO NOTHING;  -- Prevents duplicate errors
    """, (row['gene_name'],))

# ✅ Commit and close connection
conn.commit()
cursor.close()
conn.close()

print(f"✅ Genes table populated successfully! Database: {DB_PATH}")
