import sqlite3
import json
import os
import pandas as pd

DB_PATH = 'data/db/hipica_data.db'
JSON_PATH = 'data/predicciones_activas.json'

def verify_db():
    print("🔍 Verifying SQLite Database...")
    if not os.path.exists(DB_PATH):
        print("❌ Database not found!")
        return False
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check for Hippodrome in hipodromos table
    cursor.execute("SELECT * FROM hipodromos WHERE nombre LIKE '%Concepción%'")
    hip = cursor.fetchone()
    if hip:
        print(f"✅ Hippodrome Found in DB: {hip}")
    else:
        print("❌ Hippodrome 'Club Hípico de Concepción' NOT found in 'hipodromos' table.")

    # Check for Program entries
    cursor.execute("SELECT count(*) FROM programa_carreras WHERE hipodromo LIKE '%Concepción%'")
    count = cursor.fetchone()[0]
    
    if count > 0:
        print(f"✅ Found {count} program entries for Concepción.")
    else:
        print("❌ No program entries found for Concepción.")
        
    conn.close()
    return count > 0

def verify_json():
    print("\n🔍 Verifying JSON Output...")
    if not os.path.exists(JSON_PATH):
        print(f"❌ JSON file not found at {JSON_PATH}")
        return False
        
    try:
        with open(JSON_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        conce_preds = [p for p in data if 'Concepción' in p.get('hipodromo', '')]
        
        if conce_preds:
            print(f"✅ Found {len(conce_preds)} predictions for Concepción in JSON.")
            print("Sample Prediction:")
            print(json.dumps(conce_preds[0], indent=2, ensure_ascii=False))
        else:
            print("❌ No predictions for Concepción found in JSON.")
            return False
            
    except Exception as e:
        print(f"❌ Error reading JSON: {e}")
        return False
        
    return True

if __name__ == "__main__":
    db_ok = verify_db()
    json_ok = verify_json()
    
    if db_ok and json_ok:
        print("\n🎉 VERIFICATION SUCCESSFUL!")
    else:
        print("\n⚠️ VERIFICATION FAILED.")
