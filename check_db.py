import sqlite3
from datetime import datetime

# Conectar a la base de datos
conn = sqlite3.connect('hipica_data.db')
cursor = conn.cursor()

# Verificar datos del 15 de diciembre
print("=" * 60)
print("VERIFICACIÓN DE DATOS 2025-12-15")
print("=" * 60)

cursor.execute('SELECT COUNT(*) FROM programas WHERE fecha = "2025-12-15"')
total = cursor.fetchone()[0]
print(f"\nTotal registros 2025-12-15: {total}")

if total > 0:
    cursor.execute('''
        SELECT hipodromo, carrera, COUNT(*) as caballos
        FROM programas 
        WHERE fecha = "2025-12-15"
        GROUP BY hipodromo, carrera
        ORDER BY hipodromo, carrera
    ''')
    print("\nDesglose por carrera:")
    for row in cursor.fetchall():
        print(f"  {row[0]} - Carrera {row[1]}: {row[2]} caballos")

# Verificar fechas disponibles en programas
print("\n" + "=" * 60)
print("FECHAS DISPONIBLES EN PROGRAMAS")
print("=" * 60)

cursor.execute('''
    SELECT DISTINCT fecha, hipodromo, COUNT(*) as total
    FROM programas
    GROUP BY fecha, hipodromo
    ORDER BY fecha DESC
    LIMIT 10
''')

print("\nÚltimas 10 fechas:")
for row in cursor.fetchall():
    print(f"  {row[0]} - {row[1]}: {row[2]} caballos")

conn.close()
print("\n" + "=" * 60)
