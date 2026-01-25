"""
Script para verificar estado de carreras en SQLite vs Supabase.
"""
import sqlite3
import os
import sys
sys.path.append(os.path.dirname(__file__))
from src.utils.supabase_client import SupabaseManager

DB_PATH = 'data/db/hipica_data.db'

def main():
    print("=== DIAGNÓSTICO DE FOREIGN KEYS ===\n")
    
    # SQLite
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM carreras")
    sqlite_carreras = cursor.fetchone()[0]
    print(f"📦 Carreras en SQLite: {sqlite_carreras}")
    
    cursor.execute("SELECT MIN(id), MAX(id) FROM carreras")
    min_id, max_id = cursor.fetchone()
    print(f"   ID range: {min_id} - {max_id}")
    
    cursor.execute("SELECT DISTINCT carrera_id FROM participaciones ORDER BY carrera_id LIMIT 10")
    p_carrera_ids = [r[0] for r in cursor.fetchall()]
    print(f"   Participaciones -> carrera_ids (primeros 10): {p_carrera_ids}")
    
    conn.close()
    
    # Supabase
    client = SupabaseManager()
    supabase = client.get_client()
    
    if supabase:
        count_res = supabase.table('carreras').select('*', count='exact', head=True).execute()
        print(f"\n☁️ Carreras en Supabase: {count_res.count}")
        
        if count_res.count and count_res.count > 0:
            sample = supabase.table('carreras').select('id, numero, jornada_id').order('id', desc=True).limit(5).execute()
            print("   Últimas 5 carreras en Supabase:")
            for c in sample.data:
                print(f"     ID: {c['id']}, Numero: {c['numero']}, Jornada: {c['jornada_id']}")
        else:
            print("   ⚠️ No hay carreras en Supabase!")
        
        # Verificar caballos
        cab_res = supabase.table('caballos').select('*', count='exact', head=True).execute()
        print(f"\n🐴 Caballos en Supabase: {cab_res.count}")
        
        # Verificar jinetes  
        jin_res = supabase.table('jinetes').select('*', count='exact', head=True).execute()
        print(f"🏇 Jinetes en Supabase: {jin_res.count}")

if __name__ == "__main__":
    main()
