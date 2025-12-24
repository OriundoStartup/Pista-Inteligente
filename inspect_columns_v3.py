import sqlite3
import pandas as pd
import os

db_path = 'data/db/hipica_data.db'
conn = sqlite3.connect(db_path)

def check_table(name):
    try:
        df = pd.read_sql(f"SELECT * FROM {name} LIMIT 1", conn)
        print(f"\n--- {name} Columns ---")
        print(df.columns.tolist())
        # Check for preparador variants
        prep_cols = [c for c in df.columns if 'prep' in c.lower()]
        if prep_cols:
            print(f"Potential Trainer cols: {prep_cols}")
    except Exception as e:
        print(f"Error reading {name}: {e}")

check_table('participaciones')
check_table('resultados') # Legacy table
check_table('caballos')
check_table('programas') # Just in case
check_table('programa_carreras') # Just in case

conn.close()
