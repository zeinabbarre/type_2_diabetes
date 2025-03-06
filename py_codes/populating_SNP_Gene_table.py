import pandas as pd
import sqlite3
import os

# ✅ Define Base Directory (move up one level to reach the root project folder)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DB_PATH = os.path.join(BASE_DIR, "instance", "db.db")  # ✅ Universal database path
CSV_PATH = os.path.join(BASE_DIR, "csv_files", "snp_gene.csv")  # ✅ Universal CSV path

# ✅ Load CSV file
df = pd.read_csv(CSV_PATH)

# ✅ Connect to SQLite database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# ✅ Insert SNP-Gene relationships
for index, row in df.iterrows():
    # Get snp_id
    cursor.execute("SELECT snp_id FROM SNPs WHERE snp_name = ?", (row['snp_name'],))
    snp_result = cursor.fetchone()
    
    # Get gene_id
    cursor.execute("SELECT gene_id FROM Genes WHERE gene_name = ?", (row['gene_name'],))
    gene_result = cursor.fetchone()
    
    if snp_result and gene_result:
        snp_id = snp_result[0]
        gene_id = gene_result[0]
        
        # ✅ Insert into SNP_Gene table
        cursor.execute("INSERT OR IGNORE INTO SNP_Gene (snp_id, gene_id) VALUES (?, ?)", (snp_id, gene_id))

# ✅ Commit and close connection
conn.commit()
cursor.close()
conn.close()

print("✅ SNP-Gene mappings inserted successfully!")

