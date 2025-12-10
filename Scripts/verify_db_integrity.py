import sqlite3
import pandas as pd

def verify_db():
    conn = sqlite3.connect('../data/db/hipica_data.db')
    cursor = conn.cursor()

    print("=== DATABASE INTEGRITY REPORT ===\n")

    # 1. Total Counts
    cursor.execute("SELECT count(*) FROM programa_carreras")
    total_prog = cursor.fetchone()[0]
    print(f"Total Rows in programa_carreras: {total_prog}")

    cursor.execute("SELECT count(*) FROM caballos")
    print(f"Total Horses (Unique): {cursor.fetchone()[0]}")

    cursor.execute("SELECT count(*) FROM jinetes")
    print(f"Total Jockeys (Unique): {cursor.fetchone()[0]}")

    cursor.execute("SELECT count(*) FROM studs")
    print(f"Total Studs (Unique): {cursor.fetchone()[0]}")

    print("\n--- Coverage by Date & Hippodrome ---")
    cursor.execute("SELECT fecha, hipodromo, count(*) FROM programa_carreras GROUP BY fecha, hipodromo ORDER BY fecha")
    for row in cursor.fetchall():
        print(f"Date: {row[0]} | Track: {row[1]} | Races/Entries: {row[2]}")

    print("\n--- NULL Value Checks ---")
    cursor.execute("SELECT count(*) FROM programa_carreras WHERE caballo_id IS NULL OR caballo_id = ''")
    null_horses = cursor.fetchone()[0]
    print(f"Entries with missing Horse ID: {null_horses}")

    cursor.execute("SELECT count(*) FROM programa_carreras WHERE jinete_id IS NULL OR jinete_id = ''")
    null_jockeys = cursor.fetchone()[0]
    print(f"Entries with missing Jockey ID: {null_jockeys}")
    
    # 2. Data Sampling (Join Check)
    print("\n--- Data Sample (First 15 Valid Entries) ---")
    print(f"{'ID':<6} | {'Date':<10} | {'Track':<20} | {'Race':<4} | {'Horse':<25} | {'Jockey':<20}")
    print("-" * 100)
    
    query = """
    SELECT pc.id, pc.fecha, pc.hipodromo, pc.nro_carrera, c.nombre, j.nombre 
    FROM programa_carreras pc 
    LEFT JOIN caballos c ON pc.caballo_id=c.id 
    LEFT JOIN jinetes j ON pc.jinete_id=j.id 
    WHERE pc.fecha >= '2025-12-01'
    ORDER BY pc.fecha, pc.nro_carrera, pc.numero
    LIMIT 15
    """
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        for r in rows:
            hid = str(r[0])
            date = str(r[1])
            track = str(r[2])[:20]
            race = str(r[3])
            horse = str(r[4])[:25] if r[4] else "NULL"
            jockey = str(r[5])[:20] if r[5] else "NULL"
            print(f"{hid:<6} | {date:<10} | {track:<20} | {race:<4} | {horse:<25} | {jockey:<20}")
    except Exception as e:
        print(f"Error querying sample: {e}")

    conn.close()

if __name__ == "__main__":
    verify_db()
