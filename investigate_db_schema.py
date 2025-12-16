import sqlite3
import pandas as pd
import os

db_path = 'data/db/hipica_data.db'
if not os.path.exists(db_path):
    print(f"DATABASE NOT FOUND AT {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)

print("--- TABLES ---")
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print(tables)

print("\n--- SCHEMA of programa_carreras ---")
try:
    cursor.execute("PRAGMA table_info(programa_carreras)")
    columns = cursor.fetchall()
    for col in columns:
        print(col)
except Exception as e:
    print(e)

print("\n--- SAMPLE DATA from programa_carreras ---")
try:
    df = pd.read_sql("SELECT * FROM programa_carreras LIMIT 5", conn)
    print(df.to_string())
except Exception as e:
    print(e)
    
print("\n--- SAMPLE DATA from caballos ---")
try:
    df = pd.read_sql("SELECT * FROM caballos LIMIT 5", conn)
    print(df.to_string())
except Exception as e:
    print(e)

conn.close()
