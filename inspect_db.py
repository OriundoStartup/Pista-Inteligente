import sqlite3
import pandas as pd
import os

db_path = 'data/db/hipica_data.db'
if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
try:
    print("\n--- Participaciones Columns ---")
    df = pd.read_sql("SELECT * FROM participaciones LIMIT 1", conn)
    print(df.columns.tolist())
    
    print("\n--- Preparadores Table Check ---")
    try:
        df_prep = pd.read_sql("SELECT * FROM preparadores LIMIT 1", conn)
        print(df_prep.columns.tolist())
    except Exception as e:
        print(f"Table 'preparadores' error: {e}")

    print("\n--- Caballos Table Check ---")
    df_cab = pd.read_sql("SELECT * FROM caballos LIMIT 1", conn)
    print(df_cab.columns.tolist())

except Exception as e:
    print(f"General error: {e}")
finally:
    conn.close()
