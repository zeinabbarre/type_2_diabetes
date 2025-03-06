# Group-project
Type 2 Diabetes SNP Explorer
A Flask web application for exploring SNP (Single Nucleotide Polymorphism) data related to Type 2 Diabetes in various populations. The application allows users to search SNPs by name, genomic coordinates, or gene, view population-specific SNP data, and analyze Tajima's D and Fst values.
Project Structure
Your folder structure should look like this:

type_2_diabetes/
│── instance/             # Stores the SQLite database (db.db)
│── csv_files/            # Folder for storing all CSV files
│── py_codes/             # Python scripts (avoid naming it "py codes" due to a previous mistake)
│── templates/            # HTML templates for Flask
│── static/               # Static assets like CSS, images, and JavaScript
│   ├── images/           # Stores background images and logos
│── web_application.py    # Main Flask application
│── requirements.txt      # Python dependencies
│── README.md             # Project documentation (this file)


Installation & Setup
Clone the Repository
First, navigate to the directory where you want to store the project:

cd ~/Desktop  # Change this to your desired directory
git clone 
cd type_2_diabetes

Set Up a Virtual Environment
Create and activate a virtual environment:
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
3Install Required Dependencies

pip install -r requirements.txt
If you don’t have requirements.txt, generate one:
pip freeze > requirements.txt

Set Up the Database
Navigate to the type_2_diabetes folder: cd type_2_diabetes and make a new folder called instance
mkdir instance
cd instance
sqlite3 db.db  # Create the database
Verify the database was created:
sqlite> .database
This should output the path to your db.db file, e.g.,
/Users/zeinabbarre/Desktop/type_2_diabetes/instance/db.db


Create Database Tables
Copy and paste the CREATE TABLE commands from the schema_tables.sql file (available on GitHub) into your SQLite prompt.
Make sure to include any UPDATE commands as well. This will ensure that there is no duplication of South Asia and South Asian in the drop down menu and merges them. 

The fst_values_cleaned.csv file is available via Google Drive due to its size. Download it manually and save it as:

type_2_diabetes/csv_files/fst_values_cleaned.csv

Populate the Database
Use the provided Python scripts to populate the tables in your database.

Once everything is set up, start the Flask app:

python web_application.py
You should see output like:

 * Running on http://127.0.0.1:5000
Open your browser and go to http://127.0.0.1:5000 to use the application.


You might recieve an error saying you do not have matplotlib/pandas - make sure you are in the virtual environment and have activated it.
If it still doesnt work, use pip install for the module/library not found. 


