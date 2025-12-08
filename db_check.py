import sqlite3
import pandas as pd

conn = sqlite3.connect('hipica_data.db')
cursor = conn.cursor()

print("--- Data in programa_carreras ---")
try:
    cursor.execute("""
        SELECT pc.id, pc.fecha, pc.numero, c.nombre, j.nombre 
        FROM programa_carreras pc 
        LEFT JOIN caballos c ON pc.caballo_id=c.id 
        LEFT JOIN jinetes j ON pc.jinete_id=j.id 
        LIMIT 10
    """)
    rows = cursor.fetchall()
    for r in rows:
        print(r)
except Exception as e:
    print(e)
    
print("\n--- Count ---")
cursor.execute("SELECT count(*) FROM programa_carreras")
print(cursor.fetchone())

conn.close()
