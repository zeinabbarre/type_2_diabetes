# Group-project

Create & Activate a Virtual Environment
macOS/Linux:

python3 -m venv venv
source venv/bin/activate
Windows (Command Prompt):

venv\Scripts\activate

Install dependencies
pip install -r requirements.txt


Please use the update commands at the bottom of the schema tables page once the tablesare populated to map South Asia and South Asian entries correctly. Once this is done, there should only be 1 South Asian population option in the drop down menu. The csv file used to populate the Fst_Values table is in the csv_files folder and is a google drive link due to the size of the file. Please download it and save it as fsdt_values_cleaned.csv.


Use the relevant .py codes in py_codes folder to populate the tables in the database.
To do this, make a new directory called instance in the type_2_diabetes folder. 
Create a new database in instance folder using sqlite
sqlite3 instance/db.db < schema.sql


The strucutre of your folders should be the same as this. 
Open up vscode and create a type_2_diabetes folder and in it create an instance folder. This will be the path that you will quote when asked for the database path.
The databse will 
Create the other folders - csv_files, py_codes and templates (all of them in the type_2_diabetes folder. 
In github. its called py codes but that was a mistake - save it as py_codes.
Create a static folder (not statics) within the type_2_diabetes folder. Within the statics folder, create a new folder called images. 

Open up the terminal and cd to your instance folder. e.g mine would be /Users/zeinabbarre/Desktop/type_2_diabetes/instance.
Create a new database to store all of the info using sqlite3 db.db.
Check that you have correctly created the databse by typing sqlite> .database
(my example: /Users/zeinabbarre/Desktop/type_2_diabetes/instance/db.db)

Copy the CREATE TABLES commands found in the schema tables file on Github into sqlite. Make sure to copy everything including the UPDATE commands.

