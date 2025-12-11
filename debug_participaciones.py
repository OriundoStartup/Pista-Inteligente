import sqlite3
import os

db_path = 'data/db/hipica_data.db'
if not os.path.exists(db_path):
    print("❌ DB file not found")
    exit()

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

tables = ['participaciones', 'jornadas', 'carreras', 'resultados']
print(f"Checking tables in {db_path}...")

for t in tables:
    try:
        cursor.execute(f"SELECT count(*) FROM {t}")
        print(f"✅ Table '{t}': {cursor.fetchone()[0]} rows")
    except Exception as e:
        print(f"❌ Table '{t}': Error -> {e}")

# Check recent data in participaciones
try:
    cursor.execute("""
        SELECT jor.fecha, count(*) 
        FROM participaciones p
        JOIN carreras car ON p.carrera_id = car.id
        JOIN jornadas jor ON car.jornada_id = jor.id
        GROUP BY jor.fecha
        ORDER BY jor.fecha DESC
        LIMIT 5
    """)
    print("\nRecent activity in participaciones:")
    for row in cursor.fetchall():
        print(f"  Date: {row[0]} | Count: {row[1]}")
except Exception as e:
    print(f"Failed to query recent activity: {e}")

conn.close()
