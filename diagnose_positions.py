import sqlite3
import pandas as pd

conn = sqlite3.connect('data/db/hipica_data.db')

print("=== VERIFICACIÓN DETALLADA DE POSICIONES ===")

# Verificar si 2025-12-13 tiene posiciones
print("\n[RESULTADOS] Verificando posiciones para 2025-12-13 (Hipódromo Chile):")
res_13 = pd.read_sql_query("""
    SELECT 
        j.fecha, h.nombre, count(p.id) as total_part,
        sum(CASE WHEN p.posicion IS NOT NULL THEN 1 ELSE 0 END) as con_posicion
    FROM jornadas j
    JOIN hipodromos h ON j.hipodromo_id = h.id
    JOIN carreras c ON c.jornada_id = j.id
    LEFT JOIN participaciones p ON p.carrera_id = c.id
    WHERE j.fecha = '2025-12-13'
    GROUP BY j.fecha, h.nombre
""", conn)
print(res_13.to_string(index=False))

# Verificar si 2025-12-15 tiene posiciones
print("\n[RESULTADOS] Verificando posiciones para 2025-12-15 (Club Hípico):")
res_15 = pd.read_sql_query("""
    SELECT 
        j.fecha, h.nombre, count(p.id) as total_part,
        sum(CASE WHEN p.posicion IS NOT NULL THEN 1 ELSE 0 END) as con_posicion
    FROM jornadas j
    JOIN hipodromos h ON j.hipodromo_id = h.id
    JOIN carreras c ON c.jornada_id = j.id
    LEFT JOIN participaciones p ON p.carrera_id = c.id
    WHERE j.fecha = '2025-12-15'
    GROUP BY j.fecha, h.nombre
""", conn)
print(res_15.to_string(index=False))

conn.close()
