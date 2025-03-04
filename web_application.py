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
            SELECT s.snp_id, s.snp_name, s.chr_id, s.chr_pos
            FROM SNPs s
            JOIN SNP_Gene sg ON s.snp_id = sg.snp_id
            WHERE sg.gene_id = ?
        """, (gene['gene_id'],)).fetchall()

        #Fetch distinct populations from Populations table
        populations = conn.execute("""
        SELECT DISTINCT region FROM Populations
    """).fetchall()
        populations = [pop['region'] for pop in populations]

        conn.close()
        return render_template('filtered_snps.html', snps=snps, populations=populations, query=query)
    

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

        # ✅ Fetch all unique population regions from the Populations table
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
    """Displays detailed SNP information along with mapped genes and populations (without Population column and duplicates)."""
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

    # 🔹 Get population data (without Population column) and remove duplicates
    populations = conn.execute("""
        SELECT DISTINCT p_value, sample_size 
        FROM Populations WHERE snp_id = ?
    """, (snp["snp_id"],)).fetchall()

    conn.close()
    return render_template('snp_details.html', snp=snp, mapped_genes=mapped_genes, populations=populations)


@app.route('/filter_by_population', methods=['POST'])
def filter_by_population():
    """Filters SNPs by population and displays results. Computes summary stats for Tajima's D and Fst values."""
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
        SELECT s.snp_name, s.chr_id, s.chr_pos, p.p_value, p.sample_size, s.snp_id
        FROM SNPs s
        JOIN Populations p ON s.snp_id = p.snp_id
        WHERE p.region = ? AND s.snp_id IN ({placeholders})
    """

    params = [population] + snp_ids_list
    snps = conn.execute(query, params).fetchall()

    print(f"📊 Retrieved {len(snps)} SNPs")  # Debugging print

    # ✅ Fetch mapped genes for each SNP
    mapped_genes = {}
    for snp in snps:
        genes = conn.execute("""
            SELECT g.gene_name 
            FROM SNP_Gene sg
            JOIN Genes g ON sg.gene_id = g.gene_id
            WHERE sg.snp_id = ?
        """, (snp["snp_id"],)).fetchall()
        mapped_genes[snp["snp_name"]] = [gene["gene_name"] for gene in genes]

    # ✅ Count unique SNP names
    unique_snp_names = set(snp["snp_name"] for snp in snps)

    summary_stats = {}
    tajima_plot_url = None
    fst_plot_url = None
    download_url = None

    # ✅ Always Compute Summary Stats & Plot for South Asian Population
    if population.lower() == "south asian" and snps:
        # ✅ Compute Tajima's D Summary Stats
        stats_query = """SELECT tajimas_d FROM tajimas_BEB"""
        result = conn.execute(stats_query).fetchall()
        tajima_values = [row["tajimas_d"] for row in result if row["tajimas_d"] is not None]

        if tajima_values:
            summary_stats["tajimas_d"] = {
                "min": min(tajima_values),
                "max": max(tajima_values),
                "avg": np.mean(tajima_values),
                "median": np.median(tajima_values),
                "std": np.std(tajima_values)
            }

        # ✅ Compute Fst Summary Stats
        chromosome = snps[0]["chr_id"]
        start_pos = min([snp["chr_pos"] for snp in snps])
        end_pos = max([snp["chr_pos"] for snp in snps])

        fst_query = """SELECT fst_value FROM Fst_Values WHERE chromosome = ? AND position BETWEEN ? AND ?"""
        fst_result = conn.execute(fst_query, (chromosome, start_pos, end_pos)).fetchall()
        fst_values = [row["fst_value"] for row in fst_result if row["fst_value"] is not None]

        if fst_values:
            summary_stats["fst"] = {
                "min": min(fst_values),
                "max": max(fst_values),
                "avg": np.mean(fst_values),
                "median": np.median(fst_values),
                "std": np.std(fst_values)
            }

        print("✅ Summary Statistics Computed:", summary_stats)  # Debugging print

        # ✅ Save summary statistics as a text file
        static_dir = os.path.join(os.getcwd(), "static")
        os.makedirs(static_dir, exist_ok=True)

        summary_file_path = os.path.join(static_dir, "summary_statistics.txt")
        with open(summary_file_path, "w") as f:
            f.write("Tajima's D & Fst Summary Statistics\n")
            for key, values in summary_stats.items():
                f.write(f"{key.upper()} Summary:\n")
                for stat, value in values.items():
                    f.write(f"{stat.title()}: {value:.3f}\n")
                f.write("\n")

        download_url = url_for("download_summary")

        # ✅ Generate Plots
        tajima_plot_url = url_for('tajimas_image', chromosome=chromosome, start=start_pos, end=end_pos)
        fst_plot_url = url_for('fst_image', chromosome=chromosome, start=start_pos, end=end_pos)

    conn.close()

    return render_template(
        'population_snps.html',
        snps=snps,
        region=population,
        unique_snp_count=len(unique_snp_names),
        mapped_genes=mapped_genes,
        summary_stats=summary_stats,  
        tajima_plot_url=tajima_plot_url,  
        fst_plot_url=fst_plot_url,  
        download_url=download_url  
    )

@app.route('/fst_image')
def fst_image():
    """Generates and serves the Fst plot for a given chromosome and range."""
    chrom = request.args.get('chromosome', type=int)
    start_pos = request.args.get('start', type=int)
    end_pos = request.args.get('end', type=int)

    if not chrom or not start_pos or not end_pos:
        return jsonify({"error": "Missing parameters"}), 400

    img = plot_fst_values(chrom, start_pos, end_pos)
    return send_file(img, mimetype='image/png')


def plot_fst_values(chromosome, start_pos, end_pos):
    """Generates an Fst plot for the given chromosome range."""
    conn = get_db_connection()
    query = """
    SELECT position, fst_value 
    FROM Fst_Values 
    WHERE chromosome = ? AND position BETWEEN ? AND ?
    ORDER BY position;
    """

    df = pd.read_sql_query(query, conn, params=(chromosome, start_pos, end_pos))
    conn.close()

    if df.empty:
        return None  

    plt.figure(figsize=(10, 5))
    plt.scatter(df["position"], df["fst_value"], c="purple", alpha=0.7, label="Fst Values")
    plt.axhline(y=0, color="black", linestyle="--", label="Neutral Selection")
    plt.xlabel("Genomic Position (bp)")
    plt.ylabel("Fst Value")
    plt.title(f"Fst Plot - Chromosome {chromosome} ({start_pos}-{end_pos})")
    plt.legend()
    plt.grid(True)

    img = io.BytesIO()
    plt.savefig(img, format='png')
    plt.close()
    img.seek(0)

    return img


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


@app.route('/tajimas_image')
def tajimas_image():
    """Generates and serves separate Tajima's D plot images for both Punjabi and Bengali populations."""
    chrom = request.args.get('chromosome', type=int)
    start_pos = request.args.get('start', type=int)
    end_pos = request.args.get('end', type=int)

    if not chrom or not start_pos or not end_pos:
        return jsonify({"error": "Missing parameters"}), 400

    # Generate the separate Tajima’s D plot
    img = plot_tajimas_separate(chrom, start_pos, end_pos)

    # Serve the generated image
    return send_file(img, mimetype='image/png')



# Function to Generate the Tajima's D Plot (Helper Function)
def plot_tajimas_separate(chromosome, start_pos, end_pos):
    """Generate and return separate Tajima's D plots for Punjabi (PJL) and Bengali (BEB) populations."""

    # Fetch data for both populations
    df_pjl = get_tajimas(chromosome, start_pos, end_pos, "tajimas_pjl")
    df_beb = get_tajimas(chromosome, start_pos, end_pos, "tajimas_BEB")

    # Create the figure and axes
    fig, axes = plt.subplots(2, 1, figsize=(10, 10))  # Create two subplots vertically

    # Plot for Punjabi (PJL)
    if not df_pjl.empty:
        axes[0].plot(df_pjl["bin_start"], df_pjl["tajimas_d"], marker="o", linestyle="-", color="blue", label="Punjabi (Lahore)")
        axes[0].axhline(y=0, color="black", linestyle="--", label="Neutral Selection")
        axes[0].set_title(f"Tajima's D for Punjabi (PJL) - Chromosome {chromosome} ({start_pos}-{end_pos})")
        axes[0].set_xlabel("Genomic Position (bp)")
        axes[0].set_ylabel("Tajima's D")
        axes[0].legend()

    # Plot for Bengali (BEB)
    if not df_beb.empty:
        axes[1].plot(df_beb["bin_start"], df_beb["tajimas_d"], marker="s", linestyle="--", color="red", label="Bengali (Bangladesh)")
        axes[1].axhline(y=0, color="black", linestyle="--", label="Neutral Selection")
        axes[1].set_title(f"Tajima's D for Bengali (BEB) - Chromosome {chromosome} ({start_pos}-{end_pos})")
        axes[1].set_xlabel("Genomic Position (bp)")
        axes[1].set_ylabel("Tajima's D")
        axes[1].legend()

    # Save the image to a BytesIO object and return it
    img = io.BytesIO()
    plt.tight_layout()  # Adjust layout to prevent overlap
    plt.savefig(img, format='png')
    plt.close()  # Close the plot to avoid display issues
    img.seek(0)

    return img


@app.route('/gene/<gene_name>')
def gene_ontology(gene_name):
    """Displays ontology terms and pathway data for a given gene using the new Ontology table."""
    conn = get_db_connection()

    # ✅ Get gene details, including gene_id
    gene = conn.execute("SELECT * FROM Genes WHERE gene_name = ?", (gene_name,)).fetchone()
    if not gene:
        conn.close()
        flash(f"Gene '{gene_name}' not found.", "error")
        return redirect(url_for('index'))

    # ✅ Fetch ontology data from the new Ontology table
    ontology = conn.execute("""
        SELECT gene_stable_id, description, gene_type, 
               molecular_function, biological_process, cellular_component, pathway
        FROM Ontology
        WHERE gene_id = ?
    """, (gene['gene_id'],)).fetchone()

    conn.close()

    # ✅ Handle missing ontology data
    if not ontology:
        flash(f"No ontology data found for gene '{gene_name}'.", "warning")
        return render_template('gene_ontology.html', gene_name=gene_name, ontology_data={}, gene_info={})

    # ✅ Organize ontology data: Split terms so they appear on separate lines
    ontology_data = {
        "Molecular Function": ontology['molecular_function'].split('; ') if ontology['molecular_function'] else [],
        "Biological Process": ontology['biological_process'].split('; ') if ontology['biological_process'] else [],
        "Cellular Component": ontology['cellular_component'].split('; ') if ontology['cellular_component'] else []
    }

    # ✅ Process Pathways (Handle None Values)
    pathway_list = ontology['pathway'].split('; ') if ontology['pathway'] else []

    # ✅ Additional gene information (Now includes pathways)
    gene_info = {
        "Stable ID": ontology['gene_stable_id'],
        "Description": ontology['description'],
        "Gene Type": ontology['gene_type'],
        "Pathways": pathway_list if pathway_list else ["No pathway data available."]
    }

    return render_template('gene_ontology.html', gene_name=gene_name, ontology_data=ontology_data, gene_info=gene_info)



if __name__ == '__main__':
    app.run(debug=True)
