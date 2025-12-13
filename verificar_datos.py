import sqlite3
import pandas as pd

# Leer el CSV
csv_path = 'exports/PROGRAMA_CHC_2025-12-15.csv'
df = pd.read_csv(csv_path)

# Contar caballos en el CSV (excluyendo header)
caballos_csv = len(df)
print(f"📊 Caballos en CSV (2025-12-15): {caballos_csv}")

# Conectar a la base de datos
conn = sqlite3.connect('data/db/hipica_data.db')
cursor = conn.cursor()

# Ver tablas disponibles
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print(f"\n📚 Tablas disponibles: {[t[0] for t in tables]}")

# Buscar en la tabla de programas
try:
    cursor.execute("SELECT COUNT(*) FROM programa_carreras WHERE fecha = '2025-12-15'")
    caballos_db = cursor.fetchone()[0]
    print(f"📊 Caballos en DB (2025-12-15): {caballos_db}")
    
    # Comparar
    if caballos_csv == caballos_db:
        print(f"\n✅ ¡CONSISTENCIA VERIFICADA! Ambos tienen {caballos_csv} caballos.")
    else:
        print(f"\n❌ INCONSISTENCIA DETECTADA:")
        print(f"   CSV: {caballos_csv} caballos")
        print(f"   DB:  {caballos_db} caballos")
        print(f"   Diferencia: {abs(caballos_csv - caballos_db)} caballos")
        
        # Mostrar detalles
        cursor.execute("""
            SELECT nro_carrera, COUNT(*) as num_caballos 
            FROM programa_carreras 
            WHERE fecha = '2025-12-15' 
            GROUP BY nro_carrera
            ORDER BY nro_carrera
        """)
        print("\n📋 Detalles por carrera en DB:")
        for carrera, num in cursor.fetchall():
            print(f"   Carrera {carrera}: {num} caballos")
            
except Exception as e:
    print(f"❌ Error consultando DB: {e}")
    
conn.close()
