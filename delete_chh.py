import sqlite3
import os

db_path = 'data/db/hipica_data.db'
if not os.path.exists(db_path):
    print("Database not found.")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Check count before
    cursor.execute("SELECT COUNT(*) FROM programa_carreras WHERE hipodromo = 'CHH'")
    count_before = cursor.fetchone()[0]
    print(f"Entries with hipodromo='CHH' before: {count_before}")

    if count_before > 0:
        cursor.execute("DELETE FROM programa_carreras WHERE hipodromo = 'CHH'")
        conn.commit()
        print(f"Deleted {count_before} rows.")
    else:
        print("No rows to delete.")
        
    # Verify
    cursor.execute("SELECT COUNT(*) FROM programa_carreras WHERE hipodromo = 'CHH'")
    count_after = cursor.fetchone()[0]
    print(f"Entries with hipodromo='CHH' after: {count_after}")

except Exception as e:
    print(f"Error: {e}")
finally:
    conn.close()

# Also delete cache
cache_path = 'data/cache_analisis.json'
if os.path.exists(cache_path):
    os.remove(cache_path)
    print(f"Removed {cache_path}")
else:
    print(f"{cache_path} not found.")
