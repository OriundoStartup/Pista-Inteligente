import sqlite3
import os
import glob

def check_duplicates():
    print("=== Checking for Duplicates in Database ===")
    conn = sqlite3.connect('../data/db/hipica_data.db')
    cursor = conn.cursor()
    
    # Check for duplicates based on Race + Horse Number
    query = """
    SELECT fecha, hipodromo, nro_carrera, numero, count(*) 
    FROM programa_carreras 
    GROUP BY fecha, hipodromo, nro_carrera, numero 
    HAVING count(*) > 1
    """
    cursor.execute(query)
    duplicates = cursor.fetchall()
    
    if duplicates:
        print(f"WARNING: Found {len(duplicates)} duplicate entries (Race + Horse Number):")
        for d in duplicates:
            print(f"  Date: {d[0]}, Track: {d[1]}, Race: {d[2]}, Number: {d[3]}, Count: {d[4]}")
    else:
        print("OK: No duplicates found based on Race + Horse Number.")

    # Check for duplicates based on Race + Horse ID (if horse_id is reliable)
    query_horse = """
    SELECT fecha, hipodromo, nro_carrera, caballo_id, count(*) 
    FROM programa_carreras 
    WHERE caballo_id IS NOT NULL AND caballo_id != ''
    GROUP BY fecha, hipodromo, nro_carrera, caballo_id 
    HAVING count(*) > 1
    """
    cursor.execute(query_horse)
    duplicates_horse = cursor.fetchall()

    if duplicates_horse:
        print(f"WARNING: Found {len(duplicates_horse)} duplicate entries (Race + Horse ID):")
        for d in duplicates_horse:
            print(f"  Date: {d[0]}, Track: {d[1]}, Race: {d[2]}, HorseID: {d[3]}, Count: {d[4]}")
    else:
        print("OK: No duplicates found based on Race + Horse ID.")

    # Check specifically for 2025-12-11
    query_2025 = "SELECT count(*) FROM programa_carreras WHERE fecha = '2025-12-11'"
    cursor.execute(query_2025)
    count_2025 = cursor.fetchone()[0]
    print(f"\n=== Verification for 2025-12-11 ===")
    print(f"Entries found for 2025-12-11: {count_2025}")

    conn.close()


def check_csv_program():
    print("\n=== Checking for CSV Program for 2025-12-11 ===")
    # Searching in current dir and exports/ and subdirectories
    search_pattern = "**/*2025-12-11*.csv"
    matches = glob.glob(search_pattern, recursive=True)
    
    if matches:
        print(f"FOUND: Found CSV files matching 2025-12-11:")
        for m in matches:
            print(f"  - {m}")
    else:
        print("WARNING: No CSV file found for 2025-12-11.")

if __name__ == "__main__":
    check_duplicates()
    check_csv_program()
