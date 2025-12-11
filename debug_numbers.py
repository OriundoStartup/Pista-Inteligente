import sqlite3
import pandas as pd

conn = sqlite3.connect('data/db/hipica_data.db')
query = "SELECT fecha, hipodromo, nro_carrera, numero FROM programa_carreras WHERE fecha = '2025-12-12' LIMIT 10"
try:
    df = pd.read_sql_query(query, conn)
    print(df)
except Exception as e:
    print(e)
conn.close()
