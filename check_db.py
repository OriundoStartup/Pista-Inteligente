import sqlite3
import pandas as pd

conn = sqlite3.connect('data/db/hipica_data.db')
cursor = conn.cursor()

print("🔍 Checking 'tiempo' column in 'participaciones'...")
cursor.execute("SELECT count(*) FROM participaciones WHERE tiempo IS NOT NULL")
count_not_null = cursor.fetchone()[0]

cursor.execute("SELECT count(*) FROM participaciones")
count_total = cursor.fetchone()[0]

print(f"✅ Records with Time: {count_not_null} / {count_total}")

if count_not_null > 0:
    print("\nSample Data:")
    df = pd.read_sql("SELECT * FROM participaciones WHERE tiempo IS NOT NULL LIMIT 5", conn)
    print(df[['id', 'tiempo', 'distancia_cpos']])
else:
    print("❌ No time data found!")

conn.close()
