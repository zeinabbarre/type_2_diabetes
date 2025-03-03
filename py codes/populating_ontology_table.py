import pandas as pd
import sqlite3

# File paths
csv_file_path = "/Users/zeinabbarre/Desktop/type_2_diabetes/csv_files/full_gene_data.csv"
db_path = "/Users/zeinabbarre/Desktop/type_2_diabetes/instance/db.db"

# ✅ Load CSV file and clean column names
df = pd.read_csv(csv_file_path)
df.columns = df.columns.str.strip()  # ✅ Remove leading/trailing spaces
df.columns = df.columns.str.lower()  # ✅ Convert column names to lowercase for consistency

# ✅ Ensure correct column names
expected_columns = {'gene name', 'gene stable id', 'description', 'gene type', 
                    'molecular_function', 'biological_process', 'cellular_component', 'pathway'}

missing_columns = expected_columns - set(df.columns)
if missing_columns:
    raise ValueError(f"❌ Missing columns in CSV: {missing_columns}")

# ✅ Connect to SQLite database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# ✅ Loop through each row and insert ontology data
for index, row in df.iterrows():
    gene_name = row['gene name'].strip()  # ✅ Ensure correct column name

    # ✅ Fetch gene_id from Genes table
    cursor.execute("SELECT gene_id FROM Genes WHERE gene_name = ?;", (gene_name,))
    gene_id_result = cursor.fetchone()

    if gene_id_result:
        gene_id = gene_id_result[0]

        # ✅ Handle missing values (replace NaN with empty string)
        molecular_function = row['molecular_function'] if pd.notna(row['molecular_function']) else ""
        biological_process = row['biological_process'] if pd.notna(row['biological_process']) else ""
        cellular_component = row['cellular_component'] if pd.notna(row['cellular_component']) else ""
        pathway = row['pathway'] if 'pathway' in df.columns and pd.notna(row['pathway']) else ""

        # ✅ Insert into Ontology table (1 row per gene)
        cursor.execute("""
            INSERT INTO Ontology (gene_id, gene_stable_id, description, gene_type, 
                                 molecular_function, biological_process, cellular_component, pathway) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """, (gene_id, row['gene stable id'], row['description'], row['gene type'], 
              molecular_function, biological_process, cellular_component, pathway))

# ✅ Commit and close connection
conn.commit()
cursor.close()
conn.close()

print("✅ Gene Ontology Terms and Pathways successfully inserted into the Ontology table!")
