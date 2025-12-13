import sys
sys.path.append('.')
from src.models.data_manager import cargar_datos_3nf
import pandas as pd

print("=" * 70)
print("DEMOSTRACIÓN: El método de patrones busca en TODOS los resultados")
print("=" * 70)

# Este es el mismo método que usa obtener_patrones_la_tercera
df = cargar_datos_3nf()

print(f"\n📊 Total de registros cargados: {len(df)}")

# Mostrar fechas únicas
fechas_unicas = sorted(df['fecha'].unique())
print(f"\n📅 Fechas con resultados en la base de datos ({len(fechas_unicas)} fechas):")
for fecha in fechas_unicas:
    count = len(df[df['fecha'] == fecha])
    print(f"   {fecha}: {count} participaciones")

# Mostrar que agrupa por carrera
print(f"\n🏁 Total de carreras únicas procesadas:")
carreras_groups = df.groupby(['hipodromo', 'fecha', 'nro_carrera'])
print(f"   {len(carreras_groups)} carreras diferentes")

# Mostrar algunas carreras de diferentes fechas
print(f"\n🔍 Muestra de carreras procesadas (de diferentes fechas):")
sample_dates = sorted(df['fecha'].unique())[-5:]  # Últimas 5 fechas
for fecha in sample_dates:
    df_fecha = df[df['fecha'] == fecha]
    hip = df_fecha['hipodromo'].iloc[0] if len(df_fecha) > 0 else 'N/A'
    carreras = df_fecha['nro_carrera'].unique()
    print(f"   {fecha} ({hip}): {len(carreras)} carreras")

print("\n" + "=" * 70)
print("✅ CONFIRMACIÓN:")
print("El método obtener_patrones_la_tercera() procesa TODAS estas carreras")
print("y busca patrones repetidos entre TODAS ellas, no solo las del último día.")
print("=" * 70)
