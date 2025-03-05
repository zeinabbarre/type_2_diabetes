import pandas as pd
import sqlite3


# File paths
csv_file_path = "/mnt/c/Users/Hp EliteBook 840 G3/OneDrive/Desktop/type_2_diabetes/csv_files/combined_TajimaD_sorted_BEB.csv"
db_path = "/mnt/c/Users/Hp EliteBook 840 G3/OneDrive/Desktop/type_2_diabetes/instance/db.db"


# Load CSV file
df = pd.read_csv(csv_file_path)


# Connect to SQLite database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()


# Loop through each row in the DataFrame and insert data into the tajimas_BEB table
for index, row in df.iterrows():
    # Extract relevant values from the row
    chrom = row['CHROM']
    bin_start = row['BIN_START']
    n_snps = row['N_SNPS']
    tajima_d = row['TajimaD']


    # Insert the row data into the tajimas_BEB table
    cursor.execute("""
        INSERT INTO tajimas_BEB (chromosome, bin_start, n_snps, tajimas_d)
        VALUES (?, ?, ?, ?);
    """, (chrom, bin_start, n_snps, tajima_d))


# Commit the changes to the database
conn.commit()


# Close the connection
cursor.close()
conn.close()


print("TajimasD results successfully inserted into the tajimas_BEB table!")
