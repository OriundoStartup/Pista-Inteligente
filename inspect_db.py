
import sqlite3
import pandas as pd
# Fix for windows unicode
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def inspect():
    conn = sqlite3.connect('data/db/hipica_data.db')
    cursor = conn.cursor()
    
    print("--- 1. Tables ---")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    print(cursor.fetchall())
    
    print("\n--- 2. Schema: programa_carreras ---")
    cursor.execute("PRAGMA table_info(programa_carreras)")
    columns = [r[1] for r in cursor.fetchall()]
    print(columns)
    
    print("\n--- 3. Data Sample (Dec 18) ---")
    try:
        df = pd.read_sql("SELECT * FROM programa_carreras WHERE fecha >= '2025-12-18' LIMIT 1", conn)
        if not df.empty:
            print(df.iloc[0].to_dict())
            if 'caballo_id' in df.columns:
                 cid = df.iloc[0]['caballo_id']
                 print(f"\nChecking Caballo ID: {cid}")
                 c_df = pd.read_sql(f"SELECT * FROM caballos WHERE id={cid}", conn)
                 print(f"Caballo Table Match: {c_df.to_dict('records')}")
        else:
            print("No data for Dec 18")
    except Exception as e:
        print(e)
    conn.close()

if __name__ == "__main__":
    inspect()
