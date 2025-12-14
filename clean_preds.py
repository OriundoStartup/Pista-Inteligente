import sqlite3
import os

conn = sqlite3.connect('data/db/hipica_data.db')
print(f"Predicciones antes: {conn.execute('SELECT count(*) FROM predicciones').fetchone()[0]}")

print("🗑️ Borrando predicciones corruptas...")
conn.execute("DELETE FROM predicciones")
conn.commit()

print(f"Predicciones despues: {conn.execute('SELECT count(*) FROM predicciones').fetchone()[0]}")
conn.close()

print("🧹 Borrando cache JSON...")
if os.path.exists('data/cache_analisis.json'):
    os.remove('data/cache_analisis.json')
    print("✅ Cache borrado.")

print("🚀 Ejecuta ahora: python sync_system.py")
