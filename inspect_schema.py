
import sqlite3
import pandas as pd
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def inspect_cols():
    conn = sqlite3.connect('data/db/hipica_data.db')
    cursor = conn.cursor()
    
    print("\n--- Schema: programa_carreras ---")
    cursor.execute("PRAGMA table_info(programa_carreras)")
    # (cid, name, type, notnull, dflt_value, pk)
    for r in cursor.fetchall():
        print(f"{r[1]} ({r[2]})")
        
    print("\n--- Data Sample (Dec 18) ---")
    try:
        # Fetch one row as dict to see keys and values
        row = cursor.execute("SELECT * FROM programa_carreras WHERE fecha >= '2025-12-18' LIMIT 1").fetchone()
        if row:
            desc = cursor.description
            row_dict = {desc[i][0]: row[i] for i in range(len(desc))}
            print(row_dict)
    except Exception as e:
        print(e)
    conn.close()

if __name__ == "__main__":
    inspect_cols()
