import sys
import os
import pandas as pd
import sqlite3

# Add src to path to import data_manager
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.models.data_manager import obtener_estadisticas_generales

def verify_stats():
    print("📊 Verificando Estadísticas de Jinetes...")
    
    # 1. Get stats from App Logic
    stats = obtener_estadisticas_generales()
    top_jinetes = stats.get('jinetes', [])
    
    if not top_jinetes:
        print("⚠️ No jinetes found in app stats.")
        return

    print(f"   • Top Jinete App: {top_jinetes[0]['jinete']} (Carreras: {top_jinetes[0]['carreras']}, Ganadas: {top_jinetes[0]['ganadas']})")

    # 2. Verify with Direct DB Query for a specific recent winner
    # Let's find a winner from Dec 19
    conn = sqlite3.connect('data/db/hipica_data.db')
    
    # Find a jockey who won on Dec 19
    query_recent_winner = """
    SELECT j.nombre, count(*) as wins
    FROM participaciones p
    JOIN jinetes j ON p.jinete_id = j.id
    JOIN carreras c ON p.carrera_id = c.id
    JOIN jornadas y ON c.jornada_id = y.id
    WHERE p.posicion = 1 AND y.fecha >= '2025-12-17'
    GROUP BY j.nombre
    ORDER BY wins DESC
    LIMIT 5
    """
    recent_winners = pd.read_sql_query(query_recent_winner, conn)
    
    print("\n🏆 Ganadores Recientes (desde 2025-12-17) en DB:")
    print(recent_winners)
    
    if recent_winners.empty:
         print("   (No hay ganadores recientes para verificar)")
         conn.close()
         return

    # Check if these wins are reflected in the total stats
    # We can't easily check 'total' without knowing the previous state, 
    # but we can check if the Application sees the total rows correctly.
    
    # Get total wins for the top recent winner from DB
    check_jinete = recent_winners.iloc[0]['nombre']
    query_total = f"""
    SELECT count(*) 
    FROM participaciones p
    JOIN jinetes j ON p.jinete_id = j.id
    WHERE p.posicion = 1 AND j.nombre = '{check_jinete}'
    """
    total_wins_db = conn.execute(query_total).fetchone()[0]
    
    # Match with App Stats
    app_stat_jinete = next((item for item in top_jinetes if item["jinete"] == check_jinete), None)
    
    print(f"\n🔍 Comparación para '{check_jinete}':")
    print(f"   • Wins en DB (Total): {total_wins_db}")
    if app_stat_jinete:
        print(f"   • Wins en App Stats: {app_stat_jinete['ganadas']}")
        
        if app_stat_jinete['ganadas'] == total_wins_db:
             print("✅ MATCH: Los datos de la app coinciden con la DB.")
        else:
             print("❌ MISMATCH: La app muestra datos diferentes (¿Cache desactualizado?)")
    else:
        print(f"   ⚠️ Jinete '{check_jinete}' no está en el Top 10 de la App (Puede ser correcto si tiene pocas carreras totales).")

    conn.close()

if __name__ == "__main__":
    verify_stats()
