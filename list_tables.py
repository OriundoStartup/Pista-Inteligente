import sqlite3

conn = sqlite3.connect('hipica_data.db')
cursor = conn.cursor()

# Obtener todas las tablas
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cursor.fetchall()]
print("Tablas disponibles:", tables)

conn.close()
