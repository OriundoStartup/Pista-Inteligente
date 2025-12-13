import sqlite3

conn = sqlite3.connect('data/db/hipica_data.db')
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM participaciones WHERE posicion IS NOT NULL")
posiciones_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM participaciones")
total_count = cursor.fetchone()[0]

cursor.execute("SELECT posicion, mandil, caballo_id FROM participaciones LIMIT 10")
samples = cursor.fetchall()

print(f'Posiciones no NULL: {posiciones_count}')
print(f'Total participaciones: {total_count}')
print(f'Samples: {samples}')

conn.close()
