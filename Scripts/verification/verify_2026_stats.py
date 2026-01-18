import sqlite3
import pandas as pd
import os

DB_PATH = r'data/db/hipica_data.db'

def verify_stats():
    if not os.path.exists(DB_PATH):
        print(f"Error: DB not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    
    query = """
    SELECT 
        j.nombre as jinete,
        p.posicion
    FROM participaciones p
    JOIN jinetes j ON p.jinete_id = j.id
    JOIN carreras c ON p.carrera_id = c.id
    JOIN jornadas jo ON c.jornada_id = jo.id
    WHERE jo.fecha >= '2026-01-01'
    """
    
    try:
        df = pd.read_sql_query(query, conn)
        
        # Aggregate
        stats = {}
        for _, row in df.iterrows():
            jinete = row['jinete']
            pos = row['posicion']
            
            if jinete not in stats:
                stats[jinete] = {'ganadas': 0, 'montes': 0}
            
            stats[jinete]['montes'] += 1
            if pos == 1:
                stats[jinete]['ganadas'] += 1
                
        # Top 5
        top_list = []
        for name, s in stats.items():
            eff = (s['ganadas'] / s['montes'] * 100) if s['montes'] > 0 else 0
            top_list.append({
                'Jinete': name,
                'Triunfos': s['ganadas'],
                'Eficiencia': round(eff, 1)
            })
            
        top_df = pd.DataFrame(top_list)
        top_df = top_df.sort_values(by='Triunfos', ascending=False).head(5)
        
        print("--- TOP 5 JINETES 2026 (Simulacion Logic Frontend) ---")
        print(top_df.to_markdown(index=False))
        
    except Exception as e:
        print(f"Error running query: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    verify_stats()
