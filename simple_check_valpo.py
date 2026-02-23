"""Simple script to count Valparaíso races"""
import sqlite3
import sys

try:
    conn = sqlite3.connect('data/db/hipica_data.db')
    c = conn.cursor()
    
    # Get duplicate races
    query = """
    SELECT j.fecha, c.numero, COUNT(*) as duplicates
    FROM carreras c
    JOIN jornadas j ON c.jornada_id = j.id
    JOIN hipodromos h ON j.hipodromo_id = h.id
    WHERE h.nombre LIKE '%Valparaíso%'
    GROUP BY j.fecha, c.numero
    HAVING COUNT(*) > 1
    ORDER BY j.fecha DESC
    LIMIT 20
    """
    
    print("CARRERAS DUPLICADAS EN VALPARAISO:")
    print("="*60)
    result = c.execute(query).fetchall()
    if result:
        for row in result:
            print(f"Fecha: {row[0]}, Carrera #{row[1]}, Duplicados: {row[2]}")
    else:
        print("No se encontraron duplicados")
    
    # Get total races per day
    query2 = """
    SELECT j.fecha, COUNT(c.id) as total_carreras
    FROM jornadas j
    JOIN hipodromos h ON j.hipodromo_id = h.id
    LEFT JOIN carreras c ON c.jornada_id = j.id
    WHERE h.nombre LIKE '%Valparaíso%'
    GROUP BY j.id, j.fecha
    ORDER BY j.fecha DESC
    LIMIT 10
    """
    
    print("\n\nTOTAL DE CARRERAS POR DIA:")
    print("="*60)
    result2 = c.execute(query2).fetchall()
    for row in result2:
        print(f"Fecha: {row[0]}, Total carreras: {row[1]}")
    
    conn.close()
    
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
