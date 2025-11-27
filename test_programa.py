import sqlite3
import pandas as pd
from scraper import obtener_programa_proxima_jornada, guardar_programa_en_db

# Ejecutar la función
print("=" * 60)
print("PROBANDO obtener_programa_proxima_jornada()")
print("=" * 60)

df_programa = obtener_programa_proxima_jornada()

if not df_programa.empty:
    print(f"\n✅ Se obtuvieron {len(df_programa)} carreras")
    print("\nPrimeras 10 filas:")
    print(df_programa.head(10))
    
    # Guardar en DB
    guardar_programa_en_db(df_programa)
    
    # Verificar la tabla
    conn = sqlite3.connect('hipica_data.db')
    total = pd.read_sql('SELECT COUNT(*) as cnt FROM programa_carreras', conn)['cnt'][0]
    print(f"\n📊 Total en programa_carreras: {total}")
    
    # Mostrar algunas filas
    print("\nDatos guardados:")
    sample = pd.read_sql('SELECT * FROM programa_carreras LIMIT 5', conn)
    print(sample)
    
    conn.close()
else:
    print("❌ No se pudieron obtener datos del programa")
