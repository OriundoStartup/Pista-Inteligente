"""
Script para limpiar tracking y forzar reprocesamiento completo
"""
import sqlite3

conn = sqlite3.connect('data/db/hipica_data.db')
cursor = conn.cursor()

print("🗑️ Limpiando tracking de archivos procesados...")
cursor.execute("DELETE FROM archivos_procesados")
conn.commit()

count = cursor.execute("SELECT COUNT(*) FROM archivos_procesados").fetchone()[0]
print(f"✅ Archivos en tracking: {count}")

conn.close()

print("\n✅ Listo para reprocesar todos los archivos")
print("Ejecutar: python sync_system.py")
