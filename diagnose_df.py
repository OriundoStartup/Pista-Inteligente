import pandas as pd
import sys
import os

# Add src to path to import data_manager
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.models.data_manager import cargar_datos_3nf

def check_df_duplicates():
    print("🔍 Analizando DataFrame de 'cargar_datos_3nf'...")
    try:
        df = cargar_datos_3nf()
        print(f"   • Filas totales: {len(df)}")
        
        if df.empty:
            print("   ⚠️ DataFrame vacío.")
            return

        # Check for duplicate participation rows
        # A horse should appear only once per race
        dupes = df[df.duplicated(subset=['hipodromo', 'fecha', 'nro_carrera', 'caballo'], keep=False)]
        
        if not dupes.empty:
            print(f"\n❌ ALERT: {len(dupes)} filas duplicadas encontradas en el DataFrame cargado!")
            print(dupes.sort_values(['fecha', 'nro_carrera', 'caballo']).head(10)[['fecha', 'hipodromo', 'nro_carrera', 'caballo', 'posicion']])
        else:
            print("\n✅ DataFrame: OK (No duplicates found via cargar_datos_3nf)")
            
    except Exception as e:
        print(f"❌ Error loading DF: {e}")

if __name__ == "__main__":
    check_df_duplicates()
