import pandas as pd
import sqlite3

# Define file paths
csv_file_path = "/Users/zeinabbarre/Desktop/type_2_diabetes/csv_files/unique_snps.csv"
db_path = "/Users/zeinabbarre/Desktop/type_2_diabetes/instance/db.db"

# Load CSV file into pandas DataFrame
df = pd.read_csv(csv_file_path)

# Connect to SQLite database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Insert SNP data into SNPs table
for index, row in df.iterrows():
    cursor.execute("""
        INSERT INTO SNPs (snp_name, chr_id, chr_pos)
        VALUES (?, ?, ?)
        ON CONFLICT(snp_name) DO NOTHING;  -- Avoid duplicates
    """, (row['snp_name'], row['chr_id'], row['chr_pos']))

# Commit changes and close connection
conn.commit()
cursor.close()
conn.close()

print("SNP data successfully inserted into db.db!")
