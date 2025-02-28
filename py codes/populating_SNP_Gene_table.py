import pandas as pd
import sqlite3

# File paths
csv_file_path = "/Users/zeinabbarre/Desktop/type_2_diabetes/csv_files/snp_gene.csv"
db_path = "/Users/zeinabbarre/Desktop/type_2_diabetes/instance/db.db"

# Load CSV file
df = pd.read_csv(csv_file_path)

# Connect to SQLite
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Insert SNP-Gene relationships
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
        
        # Insert into SNP_Gene table
        cursor.execute("INSERT OR IGNORE INTO SNP_Gene (snp_id, gene_id) VALUES (?, ?)", (snp_id, gene_id))

# Commit and close
conn.commit()
cursor.close()
conn.close()

print("✅ SNP-Gene mappings inserted successfully!")
