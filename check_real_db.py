import sqlite3

# Usar la base de datos correcta
nombre_db = 'data/db/hipica_data.db'
conn = sqlite3.connect(nombre_db)
cursor = conn.cursor()

print("=" * 70)
print(f"VERIFICANDO: {nombre_db}")
print("=" * 70)

# Obtener todas las tablas
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cursor.fetchall()]
print("\nTablas disponibles:", tables)

# Verificar datos del 15 de diciembre en programa_carreras
if 'programa_carreras' in tables:
    print("\n" + "=" * 70)
    print("VERIFICACIÓN PROGRAMA 2025-12-15")
    print("=" * 70)
    
    cursor.execute('SELECT COUNT(*) FROM programa_carreras WHERE fecha = "2025-12-15"')
    total = cursor.fetchone()[0]
    print(f"\nTotal registros 2025-12-15: {total}")
    
    if total > 0:
        cursor.execute('''
            SELECT hipodromo, nro_carrera, COUNT(*) as caballos
            FROM programa_carreras 
            WHERE fecha = "2025-12-15"
            GROUP BY hipodromo, nro_carrera
            ORDER BY hipodromo, nro_carrera
        ''')
        print("\nDesglose por carrera:")
        for row in cursor.fetchall():
            print(f"  {row[0]} - Carrera {row[1]}: {row[2]} caballos")
    
    # Verificar fechas futuras disponibles
    print("\n" + "=" * 70)
    print("FECHAS FUTURAS EN PROGRAMA_CARRERAS (>=2025-12-13)")
    print("=" * 70)
    
    cursor.execute('''
        SELECT DISTINCT fecha, hipodromo, COUNT(*) as total
        FROM programa_carreras
        WHERE fecha >= "2025-12-13"
        GROUP BY fecha, hipodromo
        ORDER BY fecha ASC
    ''')
    
    print("\nProgramas futuros:")
    for row in cursor.fetchall():
        print(f"  {row[0]} - {row[1]}: {row[2]} caballos")

conn.close()
print("\n" + "=" * 70)
