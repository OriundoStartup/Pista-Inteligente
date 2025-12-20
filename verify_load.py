import sqlite3
import os

db_path = 'data/db/hipica_data.db'
if not os.path.exists(db_path):
    print(f"❌ Database not found at {db_path}")
    exit(1)

try:
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    print(f"🔍 Verifying data for 2025-12-19...")

    # 1. Check Journals
    c.execute("SELECT count(*) FROM jornadas WHERE fecha = '2025-12-19'")
    jornadas_count = c.fetchone()[0]
    print(f"   • Jornadas encontradas: {jornadas_count}")

    # 2. Check Participations
    c.execute("""
        SELECT count(*) 
        FROM participaciones p 
        JOIN carreras c ON p.carrera_id = c.id 
        JOIN jornadas j ON c.jornada_id = j.id 
        WHERE j.fecha = '2025-12-19'
    """)
    part_count = c.fetchone()[0]
    print(f"   • Participaciones (Resultados) cargados: {part_count}")

    # 3. Check processed files
    c.execute("SELECT nombre_archivo FROM archivos_procesados WHERE nombre_archivo LIKE '%2025-12-19%'")
    files = [r[0] for r in c.fetchall()]
    print(f"   • Archivos procesados del día: {files}")

    conn.close()

except Exception as e:
    print(f"❌ Error querying database: {e}")
