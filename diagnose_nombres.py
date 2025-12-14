import sqlite3
import pandas as pd

conn = sqlite3.connect('data/db/hipica_data.db')

print("=== CHECK NOMBRES ===")
fecha = '2025-12-13'

print("\n[PREDICCIONES] Valores únicos de hipodromo:")
preds = pd.read_sql_query(f"SELECT DISTINCT hipodromo FROM predicciones WHERE fecha_carrera='{fecha}'", conn)
print(preds)
if not preds.empty:
    val_p = preds['hipodromo'].iloc[0]
    print(f"Repr Predicciones: {repr(val_p)}")

print("\n[PROGRAMA] Valores únicos de hipodromo:")
prog = pd.read_sql_query(f"SELECT DISTINCT hipodromo FROM programa_carreras WHERE fecha='{fecha}'", conn)
print(prog)
if not prog.empty:
    val_pc = prog['hipodromo'].iloc[0]
    print(f"Repr Programa: {repr(val_pc)}")

    if not preds.empty:
        print(f"\nSon iguales? {val_p == val_pc}")

conn.close()
