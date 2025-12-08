import sqlite3
import pandas as pd

def inspect():
    conn = sqlite3.connect('hipica_data.db')
    query = """
    SELECT pc.fecha, pc.numero as num_cab, pc.caballo_id, c.nombre as nombre_caballo
    FROM programa_carreras pc
    LEFT JOIN caballos c ON pc.caballo_id = c.id
    WHERE pc.fecha = '2025-12-07'
    LIMIT 20
    """
    df = pd.read_sql(query, conn)
    print(df)
    conn.close()

if __name__ == "__main__":
    inspect()
