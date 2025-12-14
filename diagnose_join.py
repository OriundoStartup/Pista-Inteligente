import sqlite3
import pandas as pd

conn = sqlite3.connect('data/db/hipica_data.db')

print("=== DIAGNÓSTICO JOIN ===")
fecha = '2025-12-13'

print(f"\n1. Predicciones para {fecha}:")
preds = pd.read_sql_query(f"SELECT hipodromo, count(*) FROM predicciones WHERE fecha_carrera='{fecha}' GROUP BY hipodromo", conn)
print(preds)

print(f"\n2. Programa Carreras para {fecha}:")
prog = pd.read_sql_query(f"SELECT hipodromo, count(*) FROM programa_carreras WHERE fecha='{fecha}' GROUP BY hipodromo", conn)
print(prog)

print(f"\n3. Participaciones para {fecha}:")
part = pd.read_sql_query(f"""
    SELECT h.nombre, count(p.id) 
    FROM jornadas j 
    JOIN hipodromos h ON j.hipodromo_id=h.id 
    JOIN carreras c ON c.jornada_id=j.id 
    JOIN participaciones p ON p.carrera_id=c.id 
    WHERE j.fecha='{fecha}' 
    GROUP BY h.nombre
""", conn)
print(part)

print(f"\n4. JOIN Predicciones <-> Programa:")
join_pp = pd.read_sql_query(f"""
    SELECT p.hipodromo, count(*)
    FROM predicciones p
    JOIN programa_carreras pc 
        ON p.fecha_carrera = pc.fecha 
        AND p.hipodromo = pc.hipodromo 
        AND p.nro_carrera = pc.nro_carrera
        AND p.numero_caballo = pc.numero
    WHERE p.fecha_carrera='{fecha}'
    GROUP BY p.hipodromo
""", conn)
print(join_pp)

print(f"\n5. JOIN Programa <-> Participaciones (vía Caballos):")
# Esto es complejo porque programa no tiene ID directo a carrera/participacion, se hace por atributos
join_prog_part = pd.read_sql_query(f"""
    SELECT pc.hipodromo, count(*)
    FROM programa_carreras pc
    JOIN caballos c ON pc.caballo_id = c.id
    JOIN participaciones part ON part.caballo_id = c.id
    JOIN carreras car ON part.carrera_id = car.id
    JOIN jornadas jor ON car.jornada_id = jor.id
    WHERE pc.fecha='{fecha}' 
      AND jor.fecha='{fecha}'
      AND part.posicion IS NOT NULL
    GROUP BY pc.hipodromo
""", conn)
print(join_prog_part)

conn.close()
