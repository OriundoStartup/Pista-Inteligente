import sys
import pandas as pd
from datetime import datetime
from src.models.data_manager import cargar_programa, obtener_analisis_jornada

print("--- DEBUGGING DATE LOGIC ---")
from datetime import timedelta
chile_time = datetime.utcnow() - timedelta(hours=3)
today_str = chile_time.strftime('%Y-%m-%d')
print(f"UTC: {datetime.utcnow()}")
print(f"Chile Time (Calculated): {chile_time}")
print(f"Target Date String: {today_str}")

print("\n--- TEST CARGAR_PROGRAMA ---")
df = cargar_programa(solo_futuras=True)
print(f"Rows returned: {len(df)}")
if not df.empty:
    print("Columns:", df.columns.tolist())
    print("Dates in df:", df['fecha'].unique())
else:
    print("DF IS EMPTY!")

print("\n--- TEST OBTENER_ANALISIS_JORNADA ---")
# Force cache bypass manually just in case logic is weird
import os
try:
    if os.path.exists("data/cache_analisis.json"):
        print("Removing cache...")
        os.remove("data/cache_analisis.json")
except:
    pass

analisis = obtener_analisis_jornada()
print(f"Analisis returned {len(analisis)} races.")
if not analisis:
    print("Analisis is EMPTY.")
else:
    print(f"Fechas en analisis: {set(a['fecha'] for a in analisis)}")
