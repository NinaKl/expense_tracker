import sqlite3
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Directory containing the CSV files
directory = os.getenv('CSV_DIRECTORY')
name_revolut = os.getenv('REVOLUT_CSV_FILENAME')


# Connect to SQLite database for Revolut
conn = sqlite3.connect('spendings.db')

# Load CSV data into Pandas DataFrame for Revolut
revolut_data = pd.read_csv(name_revolut)
revolut_data.to_sql('revolut', conn, if_exists='replace', index=False)

##STARLING TABLE
table_name = 'starling'  # Name of the master table where all data will be combined
# Check if the table_name table already exists
cursor = conn.cursor()
query = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"
cursor.execute(query)
existing_table = cursor.fetchone()

# If 'starling' table exists, delete it
if existing_table:
    cursor.execute(f"DROP TABLE {table_name}")

# Function to import CSV data into SQLite
def import_csv_into_sqlite(csv_filename, table_name, conn):
    df = pd.read_csv(csv_filename)
    df.to_sql(table_name, conn, if_exists='append', index=False)


# Iterate through CSV files in the directory and import them into the same table in the database
for filename in os.listdir(directory):
    if filename.endswith('.csv') and filename.startswith('StarlingStatement'):
        csv_filepath = os.path.join(directory, filename)
        import_csv_into_sqlite(csv_filepath, table_name, conn)


###
### We have imported the CSV data to the SQLite database, now we have to clean them

##REVOLUT CLEANED TABLE
table_name = 'revolut_cleaned'  # Name of the master table where all data will be combined
# Check if the table_name table already exists
cursor = conn.cursor()
query_r = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"
cursor.execute(query_r)
existing_table = cursor.fetchone()

# If table exists, delete it
if existing_table:
    cursor.execute(f"DROP TABLE {table_name}")

# SQL query to create revolut_cleaned by selecting rows excluding certain descriptions
query_revolut = '''
CREATE TABLE revolut_cleaned AS
SELECT 
    strftime('%Y-%m-%d', "Started Date") AS "Date",  -- Change date format to YYYY-MM-DD
    Description AS "Merchant",  -- Rename Description column to Merchant
    Amount,
    Currency
FROM revolut
WHERE Description NOT LIKE 'To EUR%' AND Description NOT LIKE 'To GBP%' AND Description NOT LIKE 'Exchanged to GBP%' AND Description NOT LIKE 'Revolut%' AND Description NOT LIKE 'Top-Up%' AND Description NOT LIKE 'Card Top-Up'
'''

# Execute the SQL query to create revolut_cleaned
conn.execute(query_revolut)

##STARLING CLEANED TABLE
table_name = 'starling_cleaned'  # Name of the master table where all data will be combined
# Check if the table_name table already exists
cursor = conn.cursor()
query_s = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"
cursor.execute(query_s)
existing_table = cursor.fetchone()

# If table exists, delete it
if existing_table:
    cursor.execute(f"DROP TABLE {table_name}")


# SQL query to create revolut_cleaned by selecting rows excluding certain descriptions
query_starling = '''
CREATE TABLE starling_cleaned AS
SELECT 
    substr(Date, 7, 4) || '-' || substr(Date, 4, 2) || '-' || substr(Date, 1, 2) AS "Date",
    "Counter Party" AS "Merchant",
    "Amount (GBP)" AS "Amount",
    'GBP' AS "Currency"  -- Add a new 'Currency' column with value 'GBP' for each row
FROM starling
WHERE "Counter Party" NOT LIKE 'Revolut%'
'''

# Execute the SQL query to create revolut_cleaned
conn.execute(query_starling)

##ALL TOGETHER
table_name = 'all_transactions' 
cursor = conn.cursor()
query_s = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"
cursor.execute(query_s)
existing_table = cursor.fetchone()

# If table exists, delete it
if existing_table:
    cursor.execute(f"DROP TABLE {table_name}")

# Combine revolut_cleaned and starling_cleaned tables
combine_query = '''
CREATE TABLE all_transactions AS
SELECT * FROM revolut_cleaned
UNION ALL
SELECT * FROM starling_cleaned
'''

# Execute the query
conn.execute(combine_query)

##prepare a new df that we will use to display transactions per year

### spendings   ###
query_2 = "SELECT * FROM all_transactions"
data_2 = pd.read_sql_query(query_2, conn)

# Convert 'Date' column to datetime format and extract month
data_2['Date'] = pd.to_datetime(data_2['Date'])
data_2['Year'] = data_2['Date'].dt.year
data_2['Month'] = data_2['Date'].dt.to_period('M')

# Separate earnings (positive values) and spendings (negative values)
data_2['Type'] = 'Earnings'
data_2.loc[data_2['Amount'] < 0, 'Type'] = 'Spendings'

# Group data by year, month, type and sum the amounts for each month
grouped_data = data_2.groupby(['Year','Month', 'Type','Currency'])['Amount'].sum().reset_index()

##there were problems saving df to database, so we change month to string
grouped_data['Month'] = grouped_data['Month'].astype(str)

# Save grouped_data as a new table in the database
grouped_data.to_sql('grouped_transactions', conn, index=False, if_exists='replace')

#commit the changes & close the connection
conn.commit()
conn.close()

