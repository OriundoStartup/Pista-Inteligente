import pandas as pd
from rich.console import Console
from rich.table import Table
from scraper import generar_datos_simulados, obtener_datos_reales, guardar_datos_en_db
import sqlite3
import os

def cargar_datos_desde_db(nombre_db='hipica_data.db'):
    """
    Carga los datos desde la base de datos SQLite.
    """
    if not os.path.exists(nombre_db):
        print(f"Base de datos {nombre_db} no encontrada.")
        return pd.DataFrame()
        
    try:
        conn = sqlite3.connect(nombre_db)
        print(f"Cargando datos desde {nombre_db}...")
        df = pd.read_sql("SELECT * FROM resultados", conn)
        conn.close()
        return df
    except Exception as e:
        print(f"Error al cargar desde DB: {e}")
        return pd.DataFrame()

def analizar_patrones_repetidos(df):
    """
    Analiza el DataFrame para encontrar patrones de llegada repetidos.
    Muestra los resultados en una tabla usando rich.
    """
    console = Console()
    
    if df.empty:
        console.print("[bold red]No hay datos para analizar.[/bold red]")
        return

    # Contar frecuencias de 'llegada_str'
    conteo = df['llegada_str'].value_counts()
    
    # Filtrar los que se repiten más de una vez
    repetidos = conteo[conteo > 1]
    
    table = Table(title="Patrones de Llegada Repetidos (MVP)")

    table.add_column("Patrón (1-2-3)", justify="center", style="cyan", no_wrap=True)
    table.add_column("Repeticiones", justify="right", style="magenta")
    table.add_column("Detalle Carreras", justify="left", style="green")

    if repetidos.empty:
        console.print("[yellow]No se encontraron patrones repetidos en la muestra.[/yellow]")
    else:
        for patron, cantidad in repetidos.items():
            # Obtener detalles de las carreras donde ocurrió
            coincidencias = df[df['llegada_str'] == patron]
            detalles = []
            for _, row in coincidencias.iterrows():
                detalles.append(f"{row['fecha']} ({row['hipodromo']} - C{row['nro_carrera']})")
            
            # Mostrar solo los primeros 3 detalles para no saturar si hay muchos
            detalles_str = "\n".join(detalles[:3])
            if len(detalles) > 3:
                detalles_str += f"\n... y {len(detalles)-3} más"

            table.add_row(patron, str(cantidad), detalles_str)

        console.print(table)

if __name__ == "__main__":
    print("Iniciando proceso con Base de Datos SQLite...")
    
    # 1. Obtener datos (Scraping)
    # Usamos 5 días para la prueba
    df_real = obtener_datos_reales(dias_atras=5)
    
    # 2. Guardar en DB
    if not df_real.empty:
        guardar_datos_en_db(df_real)
    else:
        print("No se obtuvieron datos reales nuevos.")
        # Si no hay datos reales, para probar la DB, podríamos inyectar simulados si la DB está vacía
        if not os.path.exists('hipica_data.db'):
             print("DB no existe. Generando datos simulados para inicializar...")
             df_sim = generar_datos_simulados(10)
             guardar_datos_en_db(df_sim)

    # 3. Cargar desde DB y Analizar
    df_analisis = cargar_datos_desde_db()
    
    print(f"Analizando {len(df_analisis)} carreras...")
    analizar_patrones_repetidos(df_analisis)
