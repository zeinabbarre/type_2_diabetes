from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
import sqlite3
import re
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # ✅ Force non-GUI backend before importing pyplot
import matplotlib.pyplot as plt
import io
import os
import numpy as np

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = 'supersecretkey'  # Needed for flashed messages

# ✅ Use a relative path for the database
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'instance', 'db.db')

# ✅ Function to Establish Database Connection
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Enables dictionary-like access
    return conn

# ✅ File paths for CSV files
CSV_DIR = os.path.join(BASE_DIR, 'csv_files')
GENE_CSV_PATH = os.path.join(CSV_DIR, 'full_gene_data.csv')

# ✅ Load CSV file and clean column names
def load_gene_data():
    df = pd.read_csv(GENE_CSV_PATH)
    df.columns = df.columns.str.strip()  # ✅ Remove leading/trailing spaces
    df.columns = df.columns.str.lower()  # ✅ Convert column names to lowercase for consistency

    # ✅ Ensure correct column names
    expected_columns = {'gene name', 'gene stable id', 'description', 'gene type', 
                        'molecular_function', 'biological_process', 'cellular_component', 'pathway'}

    missing_columns = expected_columns - set(df.columns)
    if missing_columns:
        raise ValueError(f"❌ Missing columns in CSV: {missing_columns}")

    return df

# ✅ Insert ontology data into the database
def insert_ontology_data():
    df = load_gene_data()
    conn = get_db_connection()
    cursor = conn.cursor()

    for _, row in df.iterrows():
        gene_name = row['gene name'].strip()

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

    conn.commit()
    cursor.close()
    conn.close()

    print("✅ Gene Ontology Terms and Pathways successfully inserted into the Ontology table!")
