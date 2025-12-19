
import sqlite3
import pandas as pd
from datetime import datetime
import os

def check_dates():
    db_path = 'data/db/hipica_data.db'
    if not os.path.exists(db_path):
        print("DB not found")
        return

    conn = sqlite3.connect(db_path)
    
    print("--- SQLite Time Verification ---")
    # Check what SQLite thinks 'now' is
    res = conn.execute("SELECT date('now'), datetime('now'), date('now', 'localtime'), datetime('now', 'localtime')").fetchone()
    print(f"UTC Date: {res[0]}")
    print(f"UTC Time: {res[1]}")
    print(f"Local Date: {res[2]}")
    print(f"Local Time: {res[3]}")
    
    print("\n--- Program Loading Verification ---")
    # Simulate the query used in data_manager.py
    query = "SELECT fecha, nro_carrera FROM programa_carreras WHERE fecha >= date('now', 'localtime') ORDER BY fecha ASC"
    df = pd.read_sql_query(query, conn)
    
    if df.empty:
        print("No future races found with SQL filter.")
    else:
        print(f"Found {len(df)} future races.")
        print(f"Min Date: {df['fecha'].min()}")
        print(f"Max Date: {df['fecha'].max()}")
        
        # Check if any are actually in the past relative to Python's view
        today = datetime.now().strftime('%Y-%m-%d')
        past_leaks = df[df['fecha'] < today]
        if not past_leaks.empty:
            print(f"WARNING: Found {len(past_leaks)} races from the past (Python says today is {today}):")
            print(past_leaks.head())
        else:
            print("Python verification: All returned races are >= Today.")

    print("\n--- Raw Data Verification ---")
    # Check all dates available
    df_all = pd.read_sql_query("SELECT DISTINCT fecha FROM programa_carreras ORDER BY fecha DESC LIMIT 5", conn)
    print("Recent dates in DB:")
    print(df_all)

    conn.close()

if __name__ == "__main__":
    check_dates()
