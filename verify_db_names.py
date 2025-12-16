import sqlite3
import pandas as pd
import json

def verify_db():
    conn = sqlite3.connect('data/db/hipica_data.db')
    cursor = conn.cursor()

    print("\n--- Testing JOIN Logic (2025-12-15) ---")
    query = """
    SELECT 
        pc.fecha, pc.nro_carrera, pc.numero, pc.caballo_id, c.nombre as caballo_nombre
    FROM programa_carreras pc
    LEFT JOIN caballos c ON pc.caballo_id = c.id
    WHERE pc.fecha = '2025-12-18'
    ORDER BY pc.fecha DESC
    LIMIT 10
    """
    try:
        df = pd.read_sql(query, conn)
        print(df)
    except Exception as e:
        print(f"Error executing JOIN query: {e}")

    conn.close()

if __name__ == "__main__":
    verify_db()
