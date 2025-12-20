import sqlite3
import pandas as pd

def check_duplicates():
    conn = sqlite3.connect('data/db/hipica_data.db')
    
    print("🔍 Analizando Duplicados en Base de Datos...")
    
    # 1. Duplicados en Participaciones (Carrera + Caballo)
    # Buscamos si un mismo caballo (ID) corrió multiples veces en la misma carrera (ID)
    query_parts = """
    SELECT carrera_id, caballo_id, COUNT(*) as count
    FROM participaciones
    GROUP BY carrera_id, caballo_id
    HAVING count > 1
    """
    dupe_parts = pd.read_sql_query(query_parts, conn)
    if not dupe_parts.empty:
        print(f"\n❌ ALERT: {len(dupe_parts)} Participaciones duplicadas encontradas (mismo ID caballo en misma carrera):")
        print(dupe_parts.head())
    else:
        print("\n✅ Participaciones (IDs únicos): OK")

    # 2. Duplicados Logicos de Caballos (Mismo nombre, diferente ID)
    query_caballos = """
    SELECT nombre, COUNT(*) as count, GROUP_CONCAT(id) as ids
    FROM caballos
    GROUP BY nombre
    HAVING count > 1
    """
    dupe_caballos = pd.read_sql_query(query_caballos, conn)
    if not dupe_caballos.empty:
        print(f"\n⚠️ WARNING: {len(dupe_caballos)} Caballos con nombres duplicados (IDs diferentes):")
        print(dupe_caballos.head())
        
        # Check if these duplicate horses are causing duplicate participations in the same race effectively
        # e.g. Horse A (ID 1) and Horse A (ID 2) both in Race X?
        print("   -> Verificando impacto en carreras...")
        for _, row in dupe_caballos.iterrows():
            ids = row['ids'].split(',')
            if len(ids) > 1:
                # Check intersections
                q = f"""
                SELECT carrera_id, COUNT(*) as c
                FROM participaciones
                WHERE caballo_id IN ({','.join(ids)})
                GROUP BY carrera_id
                HAVING c > 1
                """
                cross_dupes = pd.read_sql_query(q, conn)
                if not cross_dupes.empty:
                    print(f"   ❌ CRITICAL: El caballo '{row['nombre']}' tiene participaciones duplicadas en {len(cross_dupes)} carreras bajo distintos IDs!")
    else:
        print("\n✅ Caballos (Nombres únicos): OK")

    conn.close()

if __name__ == "__main__":
    check_duplicates()
