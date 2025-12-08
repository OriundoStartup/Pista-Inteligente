import sqlite3
import pandas as pd

def check():
    conn = sqlite3.connect('hipica_data.db')
    # Check what dates exist
    query = "SELECT DISTINCT fecha, hipodromo, count(*) FROM programa_carreras GROUP BY fecha, hipodromo"
    df = pd.read_sql(query, conn)
    print("=== Fechas en programa_carreras ===")
    print(df)
    
    # Check sample row for 12-07
    print("\n=== Sample Row for 07-12 ===")
    c = conn.cursor()
    c.execute("SELECT * FROM programa_carreras WHERE fecha LIKE '%12-07%' OR fecha LIKE '%07/12%' LIMIT 1")
    cols = [d[0] for d in c.description]
    row = c.fetchone()
    if row:
        print(dict(zip(cols, row)))
    else:
        print("NO DATA FOUND for 12-07")
        
    conn.close()

if __name__ == "__main__":
    check()
