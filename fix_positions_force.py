import sqlite3
import pandas as pd

conn = sqlite3.connect('data/db/hipica_data.db')
cursor = conn.cursor()

print("=== FIX POSITIONS FORCE ===")

# 1. Contar antes
count_before = cursor.execute("""
    SELECT count(*) FROM participaciones 
    WHERE carrera_id IN (
        SELECT id FROM carreras WHERE jornada_id IN (
            SELECT id FROM jornadas WHERE fecha = '2025-12-13'
        )
    )
""").fetchone()[0]
print(f"Participaciones del 13/12 antes: {count_before}")

# 2. Borrar participaciones del 13
print("🗑️ Borrando participaciones del 13/12...")
cursor.execute("""
    DELETE FROM participaciones 
    WHERE carrera_id IN (
        SELECT id FROM carreras WHERE jornada_id IN (
            SELECT id FROM jornadas WHERE fecha = '2025-12-13'
        )
    )
""")
conn.commit()

# 3. Borrar tracking de resultados del 13
print("🗑️ Limpiando tracking de RESULTADOS_HC_2025-12-13...")
cursor.execute("DELETE FROM archivos_procesados WHERE nombre_archivo LIKE '%RESULTADOS_HC_2025-12-13%'")
conn.commit()

count_after = cursor.execute("""
    SELECT count(*) FROM participaciones 
    WHERE carrera_id IN (
        SELECT id FROM carreras WHERE jornada_id IN (
            SELECT id FROM jornadas WHERE fecha = '2025-12-13'
        )
    )
""").fetchone()[0]
print(f"Participaciones del 13/12 despues: {count_after}")

conn.close()
print("✅ Listo para ejecutar sync_system.py")
