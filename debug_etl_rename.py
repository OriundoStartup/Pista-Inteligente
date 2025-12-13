import pandas as pd
import sqlite3
import sys
sys.path.append('.')
from src.etl.etl_pipeline import DataCleaner

# Simular el proceso ETL exacto para el archivo problemático
file_path = 'exports/RESULTADO_CHC_2025-12-12.csv'

print("🔍 DEBUG: Simulando proceso ETL...")
print("=" * 70)

df = pd.read_csv(file_path)
print(f"\n1. Columnas originales: {list(df.columns[:10])}")

# Aplicar rename igual que en ETL (línea 342-387)
col_map = {
    'Lugar': 'posicion',
    'posicion': 'posicion',
    'lugar': 'posicion'  # Añadir lowercase también
}
df.rename(columns=col_map, inplace=True)

print(f"\n2. Después del rename: {list(df.columns[:10])}")
print(f"\n3. ¿Existe columna 'posicion'? {'posicion' in df.columns}")

if 'posicion' in df.columns:
    print(f"\n4. Primeros 5 valores de 'posicion': {df['posicion'].head().tolist()}")
    
    # Simular limpieza
    test_values = df['posicion'].head(10)
    cleaned = [DataCleaner.clean_numero(v) for v in test_values]
    print(f"\n5. Después de clean_numero: {cleaned}")
else:
    print("\n❌ ERROR: La columna 'posicion' no existe después del rename!")
    print(f"   Columnas disponibles: {list(df.columns)}")

print("\n" + "=" * 70)
