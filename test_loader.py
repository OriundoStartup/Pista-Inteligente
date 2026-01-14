import sys
import os
import pandas as pd
from datetime import datetime, timedelta

# Mock paths
sys.path.append(os.getcwd())
try:
    from src.models.data_manager import cargar_programa
except ImportError:
    # Just manual check if import fails
    import sqlite3
    def cargar_programa(solo_futuras=True):
        conn = sqlite3.connect('data/db/hipica_data.db')
        today_str = '2026-01-04'
        print(f"Querying for date >= {today_str}")
        df = pd.read_sql(f"SELECT * FROM programa_carreras WHERE fecha >= '{today_str}'", conn)
        conn.close()
        return df

def debug():
    print("Checking cargar_programa...")
    df = cargar_programa(solo_futuras=True)
    print(f"Rows found: {len(df)}")
    if not df.empty:
        print("Sample dates:")
        print(df['fecha'].unique())

if __name__ == "__main__":
    debug()
