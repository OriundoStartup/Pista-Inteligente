import sqlite3
import pandas as pd

conn = sqlite3.connect('data/db/hipica_data.db')

print("=== DIAGNÓSTICO DE MATCHES PREDICCIONES-RESULTADOS ===")

# 1. Fechas en Predicciones
fechas_pred = pd.read_sql_query("""
    SELECT DISTINCT fecha_carrera, hipodromo, count(*) as cantidad 
    FROM predicciones 
    GROUP BY fecha_carrera, hipodromo
    ORDER BY fecha_carrera
""", conn)
print("\n[PREDICCIONES] Fechas disponibles:")
print(fechas_pred.to_string(index=False))

# 2. Fechas en Resultados (Jornadas)
fechas_res = pd.read_sql_query("""
    SELECT DISTINCT j.fecha, h.nombre as hipodromo, count(c.id) as carreras
    FROM jornadas j
    JOIN hipodromos h ON j.hipodromo_id = h.id
    LEFT JOIN carreras c ON c.jornada_id = j.id
    GROUP BY j.fecha, h.nombre
    ORDER BY j.fecha DESC
    LIMIT 10
""", conn)
print("\n[RESULTADOS] Últimas jornadas cargadas:")
print(fechas_res.to_string(index=False))

# 3. Verificar coincidencia exacta de texto
print("\n[CRUCE] Verificando coincidencias exactas de fecha e hipódromo:")
query_cruce = """
SELECT 
    p.fecha_carrera as fecha_pred,
    p.hipodromo as hip_pred,
    j.fecha as fecha_res,
    h.nombre as hip_res,
    count(*) as posibles_matches
FROM predicciones p
LEFT JOIN jornadas j ON p.fecha_carrera = j.fecha 
LEFT JOIN hipodromos h ON j.hipodromo_id = h.id AND p.hipodromo = h.nombre
GROUP BY p.fecha_carrera, p.hipodromo
"""
cruce = pd.read_sql_query(query_cruce, conn)
print(cruce.to_string(index=False))

conn.close()
