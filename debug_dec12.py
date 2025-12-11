import sqlite3
import pandas as pd
import os

db_path = 'data/db/hipica_data.db'
if not os.path.exists(db_path):
    print(f"❌ DB not found at {db_path}")
    exit()

conn = sqlite3.connect(db_path)
query = "SELECT * FROM programa_carreras WHERE fecha = '2025-12-12'"
df = pd.read_sql_query(query, conn)
conn.close()

if df.empty:
    print("❌ No data found for 2025-12-12 in programa_carreras.")
    # Check what dates DO exist
    conn = sqlite3.connect(db_path)
    dates = pd.read_sql_query("SELECT DISTINCT fecha FROM programa_carreras ORDER BY fecha DESC LIMIT 5", conn)
    print("Dates found:", dates['fecha'].tolist())
    conn.close()
else:
    print(f"✅ Found {len(df)} rows for 2025-12-12.")
    print("Hipodromos:", df['hipodromo'].unique())
    print("Sample row:")
    print(df.iloc[0])
