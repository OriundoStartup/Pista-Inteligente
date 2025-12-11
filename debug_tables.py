import sqlite3

conn = sqlite3.connect('data/db/hipica_data.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables found:", [t[0] for t in tables])

for t in tables:
    table = t[0]
    try:
        cursor.execute(f"SELECT count(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"Table '{table}': {count} rows")
    except Exception as e:
        print(f"Error querying {table}: {e}")

conn.close()
