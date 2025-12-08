import pandas as pd
import os
import re

file_path = 'exports/PROGRAMA_CHC_2025-12-01.csv'

# Detectar Header Row dinámicamente
header_row = 0
try:
    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
        for i in range(10):
            line = f.readline()
            if 'Carrera' in line or 'Numero' in line or 'Cab. N' in line:
                header_row = i
                print(f"Header found at line {i}: {line.strip()}")
                break
except Exception as e:
    print(f"Error detectando header: {e}")

df = pd.read_csv(file_path, header=header_row)
print("Original Columns:", df.columns.tolist())

# Normalizar nombres de columnas (Map headers)
# Soporta formatos CHC (Cab. N°) y VSC (Numero)
col_map = {
    'Carrera': 'carrera',
    'Cab. N°': 'numero',
    'Numero': 'numero',
    'Nombre Ejemplar': 'nombre',
    'Caballo': 'nombre',
    'Jinete': 'jinete',
    'Peso': 'peso',
    'Condición Principal': 'condicion',
    'Distancia': 'distancia',
    'Hora': 'hora',
    'Stud': 'stud'
}
df.rename(columns=col_map, inplace=True)
print("Mapped Columns:", df.columns.tolist())

row = df.iloc[0]
print("\nFirst Row Data:")
print("Carrera:", row.get('carrera'))
print("Numero:", row.get('numero'))
print("Nombre:", row.get('nombre'))
print("Jinete:", row.get('jinete'))
