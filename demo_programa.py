# Script de demostración para obtener_programa_proxima_jornada()
# Este script crea datos de ejemplo simulados del programa de carreras

import pandas as pd
import sqlite3
from datetime import datetime, date, timedelta

def obtener_programa_proxima_jornada_demo():
    """Versión de demostración que crea datos simulados del programa.
    
    En producción, esta función debe ser reemplazada por scraping real
    usando Selenium para manejar el contenido dinámico de las páginas.
    """
    programa_total = []
    
    # Simular programa para Hipódromo Chile
    fecha_hch = (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')
    print(f"Generando programa demo para Hipódromo Chile ({fecha_hch})...")
    
    for carrera in range(1, 11):  # 10 carreras
        num_caballos = 12  # 12 caballos típicamente
        caballos = list(range(1, num_caballos + 1))
        
        programa_total.append({
            'fecha': fecha_hch,
            'hipodromo': 'Hipódromo Chile',
            'nro_carrera': carrera,
            'caballos': ','.join(map(str, caballos))
        })
        print(f"  -> Carrera {carrera}: {len(caballos)} caballos")
    
    # Simular programa para Club Hípico  
    fecha_ch = (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')
    print(f"\nGenerando programa demo para Club Hípico({fecha_ch})...")
    
    for carrera in range(1, 11):  # 10 carreras
        num_caballos = 10  # 10 caballos típicamente
        caballos = list(range(1, num_caballos + 1))
        
        programa_total.append({
            'fecha': fecha_ch,
            'hipodromo': 'Club Hípico',
            'nro_carrera': carrera,
            'caballos': ','.join(map(str, caballos))
        })
        print(f"  -> Carrera {carrera}: {len(caballos)} caballos")
    
    df = pd.DataFrame(programa_total)
    print(f"\n✅ Total de carreras generadas: {len(df)}")
    return df

def guardar_programa_en_db(df, nombre_db='hipica_data.db'):
    """Guarda el programa de carreras en la base de datos."""
    if df.empty:
        print("DataFrame vacío, nada que guardar.")
        return
    
    try:
        conn = sqlite3.connect(nombre_db)
        cursor = conn.cursor()
        
        # Crear tabla si no existe
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS programa_carreras (
                fecha TEXT,
                hipodromo TEXT,
                nro_carrera INTEGER,
                caballos TEXT
            )
        ''')
        conn.commit()
        
        # Limpiar la tabla antes de insertar nuevos datos
        cursor.execute('DELETE FROM programa_carreras')
        print("Limpiando datos antiguos de programa_carreras...")
        
        # Insertar nuevos datos
        print(f"Insertando {len(df)} registros en programa_carreras...")
        df.to_sql('programa_carreras', conn, if_exists='append', index=False)
        
        conn.commit()
        conn.close()
        print("✅ Programa guardado exitosamente en la base de datos.")
        
    except Exception as e:
        print(f"Error al guardar programa en base de datos: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("DEMO: Obteniendo programa de próxima jornada")
    print("=" * 60)
    
    df_programa = obtener_programa_proxima_jornada_demo()
    
    if not df_programa.empty:
        guardar_programa_en_db(df_programa)
        
        # Mostrar resumen
        print("\n" + "=" * 60)
        print("RESUMEN DEL PROGRAMA")
        print("=" * 60)
        
        conn = sqlite3.connect('hipica_data.db')
        
        # Contar carreras por hipódromo
        resumen = pd.read_sql('''
            SELECT hipodromo, fecha, COUNT(*) as num_carreras,
                   MIN(nro_carrera) as primera_carrera,
                   MAX(nro_carrera) as ultima_carrera
            FROM programa_carreras 
            GROUP BY hipodromo, fecha
        ''', conn)
        
        print("\nCarreras por hipódromo:")
        print(resumen.to_string(index=False))
        
        # Mostrar 5 carreras de ejemplo
        print("\nEjemplos de carreras:")
        ejemplo = pd.read_sql('SELECT * FROM programa_carreras LIMIT 5', conn)
        print(ejemplo.to_string(index=False))
        
        conn.close()
    else:
        print("❌ No se pudieron generar datos del programa")
