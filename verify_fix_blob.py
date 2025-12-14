import sqlite3
import pandas as pd

conn = sqlite3.connect('data/db/hipica_data.db')

print("=== VERIFICACIÓN FIX BLOBs ===")

print("Chequeando tipos de datos en predicciones:")
query = """
SELECT 
    nro_carrera, typeof(nro_carrera) as tipo_carrera,
    numero_caballo, typeof(numero_caballo) as tipo_caballo
FROM predicciones 
LIMIT 5
"""
print(pd.read_sql_query(query, conn))

conn.close()
