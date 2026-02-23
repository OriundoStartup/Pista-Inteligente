"""Simple check - is carrera 7 superfecta real?"""
import sqlite3
from src.utils.supabase_client import SupabaseManager
import json

conn = sqlite3.connect('data/db/hipica_data.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Get stored data
stored = cursor.execute("""
    SELECT prediccion_top4, resultado_top4
    FROM rendimiento_historico
    WHERE fecha = '2026-02-13' AND nro_carrera = 7
""").fetchone()

pred_stored = json.loads(stored['prediccion_top4'])
result_stored = json.loads(stored['resultado_top4'])

print("COMPARACION - Carrera 7:")
print(f"\nPrediccion: {pred_stored}")
print(f"Resultado:  {result_stored}")

# Normalize and compare
pred_norm = [p.upper().strip() for p in pred_stored]
result_norm = [r.upper().strip() for r in result_stored]

print(f"\nPrediccion (norm): {pred_norm}")
print(f"Resultado (norm):  {result_norm}")

match = pred_norm == result_norm 
print(f"\nMatch exacto: {match}")

if not match:
    print("\nDiferencias:")
    for i in range(4):
        if pred_norm[i] != result_norm[i]:
            print(f"  Pos {i+1}: '{pred_norm[i]}' != '{result_norm[i]}'")

conn.close()
