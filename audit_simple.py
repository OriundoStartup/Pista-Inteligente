"""Auditoría simplificada del sistema"""
import sqlite3
import pandas as pd
from datetime import datetime

conn = sqlite3.connect('data/db/hipica_data.db')

print("\n=== CONTEO DE REGISTROS ===")
tablas = ['archivos_procesados', 'hipodromos', 'caballos', 'jinetes', 
          'jornadas', 'carreras', 'participaciones', 'programa_carreras', 'predicciones']

for tabla in tablas:
    count = pd.read_sql_query(f"SELECT COUNT(*) as c FROM {tabla}", conn)['c'][0]
    print(f"{tabla:25} {count:8,}")

print("\n=== FECHAS EN PROGRAMAS ===")
fechas = pd.read_sql_query("""
    SELECT DISTINCT fecha, COUNT(DISTINCT nro_carrera) as carreras
    FROM programa_carreras
    GROUP BY fecha
    ORDER BY fecha DESC
    LIMIT 5
""", conn)
print(fechas.to_string())

print("\n=== ARCHIVOS PROCESADOS ===")
archivos = pd.read_sql_query("""
  SELECT COUNT(*) as total FROM archivos_procesados
""", conn)['total'][0]
print(f"Total: {archivos}")

print("\n=== VERIFICANDO DUPLICADOS EN PARTICIPACIONES ===")
dups = pd.read_sql_query("""
    SELECT COUNT(*) as total FROM (
        SELECT carrera_id, caballo_id, COUNT(*) as c
        FROM participaciones
        GROUP BY carrera_id, caballo_id
        HAVING COUNT(*) > 1
    )
""", conn)['total'][0]
print(f"Duplicados: {dups}")

conn.close()
print("\n=== AUDITORIA COMPLETADA ===")
