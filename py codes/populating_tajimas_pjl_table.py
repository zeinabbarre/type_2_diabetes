import sqlite3
import pandas as pd

# Connect to SQLite
db_path = "/Users/zeinabbarre/Desktop/type_2_diabetes/instance/db.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Load Tajima's D file
tajima_df = pd.read_csv("/Users/zeinabbarre/Desktop/type_2_diabetes/tajima_pjl.Tajima.D", sep="\t")

# Ensure column names match the `tajimas_pjl` table
tajima_df.columns = ["chromosome", "bin_start", "n_snps", "tajimas_d"]  # Adjust if needed

# Save to SQLite
tajima_df.to_sql("tajimas_pjl", conn, if_exists="append", index=False)  # ✅ Append to existing table

print("✅ Tajima's D data imported successfully into tajimas_pjl!")
conn.close()
