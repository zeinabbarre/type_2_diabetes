import sqlite3
import pandas as pd

# Database connection
db_path = "/Users/zeinabbarre/Desktop/type_2_diabetes/instance/db.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Load formatted ontology data
ontology_file = "/Users/zeinabbarre/Desktop/type_2_diabetes/csv_files/formatted_ontology_info.csv"
df = pd.read_csv(ontology_file)

# Rename column for consistency with database schema
df = df.rename(columns={"Gene name": "gene_name", "Gene stable ID": "gene_stable_id", "Gene Type": "gene_type"})

# Insert ontology data into the Ontology table
for index, row in df.iterrows():
    cursor.execute("""
        INSERT INTO Ontology (gene_id, gene_stable_id, description, gene_type, molecular_function, biological_process, cellular_component)
        SELECT gene_id, ?, ?, ?, ?, ?, ?
        FROM Genes
        WHERE gene_name = ?
    """, (row["gene_stable_id"], row["Description"], row["gene_type"], row["molecular_function"], row["biological_process"], row["cellular_component"], row["gene_name"]))

# Commit and close the connection
conn.commit()
conn.close()

print("✅ Ontology table populated successfully.")
