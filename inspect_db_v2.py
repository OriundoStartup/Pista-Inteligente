import sqlite3
import pandas as pd
import os

db_path = 'data/db/hipica_data.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

def get_columns(table):
    try:
        cursor.execute(f"PRAGMA table_info({table})")
        return [row[1] for row in cursor.fetchall()]
    except Exception as e:
        return [str(e)]

print("Participaciones:", get_columns('participaciones'))
print("Resultados:", get_columns('resultados'))
print("Caballos:", get_columns('caballos'))

conn.close()
