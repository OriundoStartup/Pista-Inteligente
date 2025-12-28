import sqlite3
import pandas as pd

def verify_db():
    db_path = 'data/db/hipica_data.db'
    conn = sqlite3.connect(db_path)
    
    # 1. Check Races for 2025-12-26
    # We join with Jornadas to get date.
    query_carreras = """
    SELECT h.nombre as hipodromo, count(c.id) as num_carreras
    FROM carreras c
    JOIN jornadas j ON c.jornada_id = j.id
    JOIN hipodromos h ON j.hipodromo_id = h.id
    WHERE j.fecha LIKE '2025-12-26%'
    GROUP BY h.nombre
    """
    
    print("🔎 Verificando Carreras en DB para 2025-12-26:")
    try:
        df_c = pd.read_sql(query_carreras, conn)
        if not df_c.empty:
            print(df_c.to_string(index=False))
        else:
            print("⚠️ No se encontraron carreras para esta fecha.")
    except Exception as e:
        print(f"❌ Error query carreras: {e}")

    # 2. Check Participations
    query_part = """
    SELECT count(p.id) as total_participaciones
    FROM participaciones p
    JOIN carreras c ON p.carrera_id = c.id
    JOIN jornadas j ON c.jornada_id = j.id
    WHERE j.fecha LIKE '2025-12-26%'
    """
    
    print("\n🔎 Verificando Participaciones en DB para 2025-12-26:")
    try:
        df_p = pd.read_sql(query_part, conn)
        print(f"Total filas: {df_p.iloc[0]['total_participaciones']}")
    except Exception as e:
        print(f"❌ Error query participaciones: {e}")
        
    conn.close()

if __name__ == "__main__":
    verify_db()
