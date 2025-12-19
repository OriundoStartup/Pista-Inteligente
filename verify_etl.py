import sys
import os
import sqlite3
from src.etl.etl_pipeline import HipicaETL

# Initialize ETL
etl = HipicaETL()
file_path = "exports/PROGRAMA_CHC_2025-12-19.CSV"

print(f"--- DEBUGGING ETL FOR {file_path} ---")

if not os.path.exists(file_path):
    print(f"❌ File not found: {file_path}")
    # Try finding it
    import glob
    print("Files in exports/:")
    for f in glob.glob("exports/*"):
        print(f"  - {f}")
    sys.exit(1)

# Check invalid processed entry
db_path = "data/db/hipica_data.db"
conn = sqlite3.connect(db_path)
fname = os.path.basename(file_path)
cursor = conn.cursor()
cursor.execute("SELECT * FROM archivos_procesados WHERE nombre_archivo=?", (fname,))
row = cursor.fetchone()
print(f"Archivos procesados entry: {row}")
conn.close()

# Run process_csv directly
print("\n--- RUNNING PROCESS_CSV ---")
try:
    processed_count = etl.process_csv(file_path)
    print(f"Processed count returned: {processed_count}")
except Exception as e:
    print(f"❌ ERROR in process_csv: {e}")
    import traceback
    traceback.print_exc()

# Verify DB after
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM programa_carreras WHERE fecha='2025-12-19'")
count = cursor.fetchone()[0]
print(f"\n--- VERIFICATION ---")
print(f"Rows in programa_carreras for 2025-12-19: {count}")
conn.close()
