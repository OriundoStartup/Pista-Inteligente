"""Investigación del problema de tablas vacías"""
import sqlite3
import pandas as pd

conn = sqlite3.connect('data/db/hipica_data.db')

print("=== TABLAS EXISTENTES ===")
tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table'", conn)
print(tables.to_string(index=False))

print("\n=== SCHEMA DE PARTICIPACIONES ===")
schema_part = pd.read_sql_query("PRAGMA table_info(participaciones)", conn)
print(schema_part.to_string())

print("\n=== SCHEMA DE PROGRAMA_CARRERAS ===")
schema_prog = pd.read_sql_query("PRAGMA table_info(programa_carreras)", conn)
print(schema_prog.to_string())

print("\n=== ÚLTIMAS 5 JORNADAS ===")
jornadas = pd.read_sql_query("""
    SELECT j.*, h.nombre as hip_nombre
    FROM jornadas j
    LEFT JOIN hipodromos h ON j.hipodromo_id = h.id
    ORDER BY j.fecha DESC
    LIMIT 5
""", conn)
print(jornadas.to_string())

print("\n=== CARRERAS POR JORNADA ===")
carreras = pd.read_sql_query("""
    SELECT jornada_id, COUNT(*) as num_carreras
    FROM carreras
    GROUP BY jornada_id
""", conn)
print(carreras.to_string())

print("\n=== PARTICIPACIONES POR CARRERA (DEBE TENER DATOS) ===")
part_count = pd.read_sql_query("""
    SELECT c.id as carrera_id, c.numero, COUNT(p.id) as participaciones
    FROM carreras c
    LEFT JOIN participaciones p ON p.carrera_id = c.id
    GROUP BY c.id, c.numero
    LIMIT 10
""", conn)
print(part_count.to_string())

conn.close()
