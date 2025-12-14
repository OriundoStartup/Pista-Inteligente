import sqlite3
import pandas as pd

conn = sqlite3.connect('data/db/hipica_data.db')

print("=== DEEP JOIN DIAGNOSIS ===")
fecha = '2025-12-13'

query = f"""
SELECT 
    p.nro_carrera as p_carrera,
    p.numero_caballo as p_numero,
    pc.nro_carrera as pc_carrera,
    pc.numero as pc_numero,
    typeof(p.nro_carrera) as type_p_carr,
    typeof(pc.nro_carrera) as type_pc_carr,
    typeof(p.numero_caballo) as type_p_num,
    typeof(pc.numero) as type_pc_num
FROM predicciones p
LEFT JOIN programa_carreras pc 
    ON p.fecha_carrera = pc.fecha 
    AND p.hipodromo = pc.hipodromo
    AND p.nro_carrera = pc.nro_carrera
WHERE p.fecha_carrera='{fecha}' 
ORDER BY p.nro_carrera, p.numero_caballo
LIMIT 10
"""

print("\nIntentando JOIN parcial (Fecha + Hip + Carrera):")
df = pd.read_sql_query(query, conn)
print(df)

if df['pc_numero'].isna().all():
    print("❌ NO matchea ni siquiera la carrera!")
    # Ver carreras disponibles en programa
    print("\nCarreras en programa:")
    print(pd.read_sql_query(f"SELECT DISTINCT nro_carrera FROM programa_carreras WHERE fecha='{fecha}' ORDER BY nro_carrera", conn))
else:
    print("\n✅ Matchea carrera. Verificando números de caballo...")
    # Ver si matchea numero
    query_full = f"""
    SELECT 
        p.nro_carrera,
        p.numero_caballo as p_num,
        pc.numero as pc_num
    FROM predicciones p
    LEFT JOIN programa_carreras pc 
        ON p.fecha_carrera = pc.fecha 
        AND p.hipodromo = pc.hipodromo
        AND p.nro_carrera = pc.nro_carrera
        AND p.numero_caballo = pc.numero
    WHERE p.fecha_carrera='{fecha}' 
    LIMIT 10
    """
    print(pd.read_sql_query(query_full, conn))

conn.close()
