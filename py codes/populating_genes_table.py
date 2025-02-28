import pandas as pd
import sqlite3

# Define file paths
csv_file_path = "/Users/zeinabbarre/Desktop/type_2_diabetes/csv_files/unique_mapped_genes.csv"
db_path = "/Users/zeinabbarre/Desktop/type_2_diabetes/instance/db.db"

# Load CSV file
df = pd.read_csv(csv_file_path)

# Remove duplicates (ensures unique genes)
df = df.drop_duplicates(subset=['gene_name'])

# Connect to SQLite database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Insert data into Genes table
for index, row in df.iterrows():
    cursor.execute("""
        INSERT INTO Genes (gene_name)
        VALUES (?)
        ON CONFLICT(gene_name) DO NOTHING;  -- Prevents duplicate errors
    """, (row['gene_name'],))

# Commit and close connection
conn.commit()
cursor.close()
conn.close()

print("Genes table populated successfully!")
