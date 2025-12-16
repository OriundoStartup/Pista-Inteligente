import sqlite3
import pandas as pd

def diagnose():
    conn = sqlite3.connect('data/db/hipica_data.db')
    target_date = '2025-12-15'
    
    print(f"--- Diagnóstico para {target_date} ---")
    
    # 1. Check Predicciones
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM predicciones WHERE fecha_carrera = ?", (target_date,))
    count_pred = c.fetchone()[0]
    print(f"1. Predicciones encontradas: {count_pred}")
    
    # 2. Check Participaciones (Results) via Jornadas
    # Need to find IDs for that status
    # query results directly
    query_res = """
    SELECT COUNT(*) 
    FROM participaciones p
    JOIN carreras c ON p.carrera_id = c.id
    JOIN jornadas j ON c.jornada_id = j.id
    WHERE j.fecha = ?
    """
    c.execute(query_res, (target_date,))
    count_res = c.fetchone()[0]
    print(f"2. Participaciones (Resultados) encontrados: {count_res}")

    # 3. Check Caballo IDs in Predicciones
    c.execute("SELECT COUNT(*) FROM predicciones WHERE fecha_carrera = ? AND caballo_id IS NOT NULL", (target_date,))
    count_pred_valid_id = c.fetchone()[0]
    print(f"3. Predicciones con caballo_id válido: {count_pred_valid_id}")

    # 4. Check PROGRAMA links (The one we fixed)
    query_prog = "SELECT COUNT(*) FROM programa_carreras WHERE fecha = ? AND caballo_id IS NOT NULL"
    c.execute(query_prog, (target_date,))
    count_prog = c.fetchone()[0]
    print(f"4. Programa Carreras con caballo_id válido: {count_prog}")

    # 5. Test the JOIN logic from data_manager.py
    print("\n5. Testing Full Join (Limit 5)...")
    full_query = """
        SELECT 
            p.numero_caballo,
            p.ranking_prediccion,
            part.posicion as posicion_real
        FROM predicciones p
        INNER JOIN programa_carreras pc 
            ON p.fecha_carrera = pc.fecha 
            AND p.hipodromo = pc.hipodromo 
            AND p.nro_carrera = pc.nro_carrera
            AND p.numero_caballo = pc.numero
        INNER JOIN caballos c ON pc.caballo_id = c.id
        INNER JOIN participaciones part ON part.caballo_id = c.id
        INNER JOIN carreras car ON part.carrera_id = car.id
        INNER JOIN jornadas jor ON car.jornada_id = jor.id
        WHERE jor.fecha = ?
    """
    try:
        df = pd.read_sql(full_query, conn, params=(target_date,))
        print(f"Rows returned by FULL JOIN: {len(df)}")
        if not df.empty:
            print(df.head())
    except Exception as e:
        print(f"Error in Full Query: {e}")

    # 6. Alternative Simpler Query Proposal
    print("\n6. Testing Simpler Join (Pred -> Caballo <- Part)...")
    simple_query = """
        SELECT 
            p.numero_caballo,
            p.ranking_prediccion,
            part.posicion as posicion_real
        FROM predicciones p
        INNER JOIN caballos c ON p.caballo_id = c.id
        INNER JOIN participaciones part ON part.caballo_id = c.id
        INNER JOIN carreras car ON part.carrera_id = car.id
        INNER JOIN jornadas jor ON car.jornada_id = jor.id
        WHERE p.fecha_carrera = ? AND jor.fecha = ?
    """
    try:
        df_simple = pd.read_sql(simple_query, conn, params=(target_date, target_date))
        print(f"Rows returned by SIMPLE JOIN: {len(df_simple)}")
    except Exception as e:
        print(f"Error in Simple Query: {e}")

    conn.close()

if __name__ == "__main__":
    diagnose()
