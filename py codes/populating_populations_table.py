import sqlite3
import pandas as pd

# Load CSV file
csv_file = "final_population.csv"  # Update with actual filename
df = pd.read_csv(csv_file)


# Connect to SQLite database
conn = sqlite3.connect("/Users/zeinabbarre/Desktop/type_2_diabetes/instance/db.db")
cursor = conn.cursor()

# Ensure Populations table exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS Populations (
    pop_id INTEGER PRIMARY KEY AUTOINCREMENT,
    snp_id INTEGER NOT NULL,
    region TEXT NOT NULL,
    p_value REAL NOT NULL,
    sample_size TEXT,
    FOREIGN KEY (snp_id) REFERENCES SNPs(snp_id) ON DELETE CASCADE
);
""")

# Insert SNPs & Populations
for _, row in df.iterrows():
    snp_name = row["SNPS"]
    region = row["REGION"]
    p_value = row["P-VALUE"]  # No changes, always keeps the value
    sample_size = row["INITIAL SAMPLE SIZE"] if pd.notna(row["INITIAL SAMPLE SIZE"]) else None

    # Check if SNP already exists in SNPs table
    cursor.execute("SELECT snp_id FROM SNPs WHERE snp_name = ?", (snp_name,))
    result = cursor.fetchone()

    if result:
        snp_id = result[0]  # Existing SNP ID
    else:
        print(f"⚠️ SNP {snp_name} not found in SNPs table. Skipping...")
        continue  # Skip inserting population data if SNP doesn't exist

    # Insert Population Data
    cursor.execute("""
        INSERT INTO Populations (snp_id, region, p_value, sample_size)
        VALUES (?, ?, ?, ?)
    """, (snp_id, region, p_value, sample_size))

# Commit & close
conn.commit()
conn.close()

print("✅ Database successfully updated with Population data!")
