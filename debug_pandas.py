import pandas as pd
import glob
import os

files = glob.glob('exports/*CHC*2025-12-01*.csv')
if files:
    f = files[0]
    print(f"Reading {f}")
    df = pd.read_csv(f)
    print("Columns:", df.columns.tolist())
    
    # Check what 'Nombre Ejemplar' maps to if cleaned
    print("Cleaned Columns:", [c.strip() for c in df.columns])
