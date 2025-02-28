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
DB_PATH = "/Users/zeinabbarre/Desktop/type_2_diabetes/instance/db.db"

# ✅ Function to Establish Database Connection
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Enables dictionary-like access
    return conn

@app.route('/')
def index():
    """Renders the homepage."""
    return render_template('index.html')

# ✅ SEARCH FUNCTIONALITY (SNP, Gene, Genomic Coordinates)
@app.route('/search_snp', methods=['POST'])
def search_snp():
    """Handles search for SNPs, genes, or genomic coordinates."""
    query = request.form['search_query'].strip()
    conn = get_db_connection()

    # 🔹 Search by SNP Name
    snp = conn.execute("""
        SELECT snp_name, chr_id, chr_pos
        FROM SNPs
        WHERE LOWER(snp_name) = LOWER(?)
    """, (query,)).fetchone()

    if snp:
        conn.close()
        return redirect(url_for('snp_details', snp_name=snp['snp_name']))

    # 🔹 Search by Gene Name
    gene = conn.execute("SELECT * FROM Genes WHERE LOWER(gene_name) = LOWER(?)", (query,)).fetchone()
    
    if gene:
        snps = conn.execute("""
            SELECT s.snp_name, s.chr_id, s.chr_pos
            FROM SNPs s
            JOIN SNP_Gene sg ON s.snp_id = sg.snp_id
            WHERE sg.gene_id = ?
        """, (gene['gene_id'],)).fetchall()

        conn.close()
        return render_template('gene_snps.html', snps=snps, gene=query)

    # 🔹 Search by Genomic Coordinates
    match = re.match(r"^(\d+):(\d+)-(\d+)$", query)
    if match:
        chromosome, start_pos, end_pos = match.groups()
        start_pos, end_pos = int(start_pos), int(end_pos)

        # ✅ Fetch SNPs in the given genomic region
        snps = conn.execute("""
            SELECT snp_id, snp_name, chr_id, chr_pos
            FROM SNPs 
            WHERE chr_id = ? AND chr_pos BETWEEN ? AND ?
        """, (chromosome, start_pos, end_pos)).fetchall()

        # ✅ Fetch all unique population regions from the `Populations` table
        populations = conn.execute("""
            SELECT DISTINCT region FROM Populations
        """).fetchall()
        populations = [pop["region"] for pop in populations]

        conn.close()

        if snps:
            return render_template('filtered_snps.html', snps=snps, populations=populations, query=query)

        flash("No SNPs found in the specified region.", "error")
        return redirect(url_for('index'))

    # 🔹 No results found
    flash("No results found.", "error")
    conn.close()
    return redirect(url_for('index'))

# ✅ SNP DETAILS PAGE
@app.route('/snp/<snp_name>')
def snp_details(snp_name):
    """Displays detailed SNP information along with mapped genes and populations."""
    conn = get_db_connection()

    # 🔹 Fetch SNP details
    snp = conn.execute("""
        SELECT * FROM SNPs WHERE snp_name = ?
    """, (snp_name,)).fetchone()

    # 🔹 If SNP is not in the SNPs table, check if it exists in Populations
    if not snp:
        pop_snp = conn.execute("""
            SELECT DISTINCT snp_id FROM Populations WHERE snp_id = (
                SELECT snp_id FROM SNPs WHERE snp_name = ?
            )
        """, (snp_name,)).fetchone()

        if pop_snp:
            snp = {"snp_name": snp_name, "chr_id": "Unknown", "chr_pos": "Unknown", "snp_id": pop_snp["snp_id"]}
        else:
            conn.close()
            flash(f"SNP '{snp_name}' not found.", "error")
            return redirect(url_for('index'))

    # 🔹 Get mapped genes (only if SNP is in `SNPs`)
    mapped_genes = []
    if isinstance(snp, sqlite3.Row) and "snp_id" in snp.keys():
        mapped_genes = conn.execute("""
            SELECT g.gene_name 
            FROM SNP_Gene sg
            INNER JOIN Genes g ON sg.gene_id = g.gene_id
            WHERE sg.snp_id = ?
        """, (snp["snp_id"],)).fetchall()

    # 🔹 Get population data (fixing the incorrect column reference)
    populations = conn.execute("""
        SELECT region, p_value, sample_size 
        FROM Populations WHERE snp_id = ?
    """, (snp["snp_id"],)).fetchall()

    conn.close()
    return render_template('snp_details.html', snp=snp, mapped_genes=mapped_genes, populations=populations)



@app.route('/filter_by_population', methods=['POST'])
def filter_by_population():
    """Filters SNPs by population and displays results. Only computes summary stats for South Asian population."""
    population = request.form.get('population')
    snp_ids = request.form.get('snp_ids')

    if not population or not snp_ids:
        flash("Invalid selection. Please choose a population.", "error")
        return redirect(url_for('index'))

    conn = get_db_connection()
    snp_ids_list = snp_ids.split(',')

    print("🚀 Processing Population:", population)
    print("📌 SNP IDs Received:", snp_ids_list)

    # ✅ Query SNPs for the selected population
    placeholders = ','.join(['?'] * len(snp_ids_list))
    query = f"""
        SELECT s.snp_name, s.chr_id, s.chr_pos, p.p_value, p.sample_size
        FROM SNPs s
        JOIN Populations p ON s.snp_id = p.snp_id
        WHERE p.region = ? AND s.snp_id IN ({placeholders})
    """

    params = [population] + snp_ids_list
    snps = conn.execute(query, params).fetchall()

    print(f"📊 Retrieved {len(snps)} SNPs")  # Debugging print

    summary_stats = None
    tajima_plot_url = None
    download_url = None

    # ✅ Only compute Tajima's D summary statistics for South Asian population
    if population.lower() == "south asian":
        stats_query = """SELECT tajimas_d FROM tajimas_BEB"""
        result = conn.execute(stats_query).fetchall()

        # ✅ Extract values and remove None
        tajima_values = [row["tajimas_d"] for row in result if row["tajimas_d"] is not None]

        if tajima_values:
            summary_stats = {
                "min_tajimas_d": min(tajima_values),
                "max_tajimas_d": max(tajima_values),
                "avg_tajimas_d": np.mean(tajima_values),
                "median_tajimas_d": np.median(tajima_values),
                "std_tajimas_d": np.std(tajima_values)
            }

            print("✅ Summary Statistics Computed:", summary_stats)  # Debugging print

            # ✅ Save summary statistics as a text file
            static_dir = os.path.join(os.getcwd(), "static")
            os.makedirs(static_dir, exist_ok=True)

            summary_file_path = os.path.join(static_dir, "summary_statistics.txt")
            with open(summary_file_path, "w") as f:
                f.write("Tajima's D Summary Statistics\n")
                for key, value in summary_stats.items():
                    f.write(f"{key.replace('_', ' ').title()}: {value:.3f}\n")

            download_url = url_for("download_summary")

            # ✅ Generate Tajima’s D plot only for South Asian SNPs
            if snps:
                chromosome = snps[0]["chr_id"]
                start_pos = min([snp["chr_pos"] for snp in snps])
                end_pos = max([snp["chr_pos"] for snp in snps])

                tajima_plot_url = url_for('tajimas_image', chromosome=chromosome, start=start_pos, end=end_pos)

    conn.close()

    # ✅ If not South Asian, return SNP table only (without stats or plots)
    if population.lower() != "south asian":
        return render_template(
            'population_snps.html',
            snps=snps,
            region=population
        )

    # ✅ If South Asian, return full details with summary stats and plot
    return render_template(
        'population_snps.html',
        snps=snps,
        region=population,
        summary_stats=summary_stats,
        tajima_plot_url=tajima_plot_url,
        download_url=download_url
    )



# ✅ Route for Downloading Summary Statistics
@app.route("/download_summary")
def download_summary():
    """Allows users to download summary statistics as a text file."""
    static_dir = os.path.join(os.getcwd(), "static")  # Ensure we're using the right directory
    summary_file_path = os.path.join(static_dir, "summary_statistics.txt")

    # ✅ Check if the file actually exists before sending it
    if not os.path.exists(summary_file_path):
        print(f"❌ ERROR: File not found at {summary_file_path}")
        return "Error: Summary statistics file not found", 404

    print(f"✅ Sending file: {summary_file_path}")
    return send_file(summary_file_path, as_attachment=True, download_name="summary_statistics.txt")

# Function to fetch Tajima's D values
def get_tajimas(chromosome, start_pos, end_pos, table_name):
    """Fetch Tajima's D values for a specific region from the given SQL table."""
    conn = sqlite3.connect(DB_PATH)  # Use the correct database path
    query = f'''
    SELECT bin_start, tajimas_d
    FROM {table_name}
    WHERE chromosome = ?
    AND bin_start BETWEEN ? AND ?
    ORDER BY bin_start;
    '''
    
    try:
        df = pd.read_sql_query(query, conn, params=(chromosome, start_pos, end_pos))
    except Exception as e:
        print(f"❌ SQL Error while querying {table_name}: {e}")
        df = pd.DataFrame()  # Return an empty DataFrame if there's an error
    finally:
        conn.close()  # Ensure the connection is properly closed

    return df  # ✅ Now it actually returns the DataFrame


# ✅ Flask Route to Serve the Plot Image
@app.route('/tajimas_image')
def tajimas_image():
    """Generates and serves Tajima's D plot image."""
    chrom = request.args.get('chromosome', type=int)
    start_pos = request.args.get('start', type=int)
    end_pos = request.args.get('end', type=int)

    if not chrom or not start_pos or not end_pos:
        return jsonify({"error": "Missing parameters"}), 400

    # Generate the Tajima’s D plot
    img = plot_tajimas_combined(chrom, start_pos, end_pos)

    # Serve the generated image
    return send_file(img, mimetype='image/png')


# ✅ Function to Generate the Tajima's D Plot (Helper Function)
def plot_tajimas_combined(chromosome, start_pos, end_pos):
    """Generate and return Tajima's D plot for Punjabi and Bengali populations."""
    
    # Fetch data
    df_pjl = get_tajimas(chromosome, start_pos, end_pos, "tajimas_pjl")
    df_beb = get_tajimas(chromosome, start_pos, end_pos, "tajimas_BEB")

    plt.figure(figsize=(10, 5))

    if not df_pjl.empty:
        plt.plot(df_pjl["bin_start"], df_pjl["tajimas_d"], marker="o", linestyle="-", color="blue", label="Punjabi (Lahore)")
    
    if not df_beb.empty:
        plt.plot(df_beb["bin_start"], df_beb["tajimas_d"], marker="s", linestyle="--", color="red", label="Bengali (Bangladesh)")

    plt.axhline(y=0, color="black", linestyle="--", label="Neutral Selection")
    plt.xlabel("Genomic Position (bp)")
    plt.ylabel("Tajima's D")
    plt.title(f"Tajima’s D Across Chromosome {chromosome} ({start_pos}-{end_pos})")
    plt.legend()
    
    img = io.BytesIO()
    plt.savefig(img, format='png')
    plt.close()
    img.seek(0)

    return img

@app.route('/gene/<gene_name>')
def gene_ontology(gene_name):
    """Displays ontology terms for a given gene."""
    conn = get_db_connection()

    gene = conn.execute("SELECT * FROM Genes WHERE gene_name = ?", (gene_name,)).fetchone()
    if not gene:
        conn.close()
        flash(f"Gene '{gene_name}' not found.", "error")
        return redirect(url_for('index'))

    ontology_terms = conn.execute("""
        SELECT go_term_type, go_term 
        FROM Gene_Ontology_Terms
        WHERE gene_id = ?
    """, (gene['gene_id'],)).fetchall()

    conn.close()

    ontology_data = {
        "Molecular Function": [row['go_term'] for row in ontology_terms if row['go_term_type'] == 'Molecular Function'],
        "Biological Process": [row['go_term'] for row in ontology_terms if row['go_term_type'] == 'Biological Process'],
        "Cellular Component": [row['go_term'] for row in ontology_terms if row['go_term_type'] == 'Cellular Component']
    }

    return render_template('gene_ontology.html', gene_name=gene_name, ontology_data=ontology_data)



if __name__ == '__main__':
    app.run(debug=True)

