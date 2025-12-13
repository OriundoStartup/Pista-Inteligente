import sqlite3
import pandas as pd
from datetime import datetime

# Conectar a la base de datos
db_path = 'data/db/hipica_data.db'
conn = sqlite3.connect(db_path)

print("=" * 80)
print("VERIFICANDO ESTRUCTURA Y DATOS DE PREDICCIONES EN LA BASE DE DATOS")
print("=" * 80)

# 1. Ver todas las tablas
print("\n📋 TABLAS EN LA BASE DE DATOS:")
print("-" * 80)
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
tables = cursor.fetchall()
for table in tables:
    print(f"  • {table[0]}")

# 2. Buscar tablas relacionadas con predicciones
print("\n\n🔍 BUSCANDO TABLAS DE PREDICCIONES:")
print("-" * 80)
prediction_tables = [t[0] for t in tables if 'pred' in t[0].lower() or 'forecast' in t[0].lower()]
if prediction_tables:
    for table in prediction_tables:
        print(f"  ✅ Tabla encontrada: {table}")
else:
    print("  ⚠️  No se encontraron tablas específicas de predicciones")

# 3. Verificar estructura de tablas principales
print("\n\n📊 ESTRUCTURA DE TABLAS PRINCIPALES:")
print("-" * 80)
for table_name in [t[0] for t in tables]:
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    print(f"\n{table_name}:")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
    
    # Contar registros
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    print(f"  Total de registros: {count}")

# 4. Buscar columnas que puedan contener predicciones
print("\n\n🎯 BUSCANDO DATOS DE PREDICCIONES EN TODAS LAS TABLAS:")
print("-" * 80)
for table_name in [t[0] for t in tables]:
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]
    
    # Buscar columnas relacionadas con predicciones
    pred_columns = [c for c in column_names if any(keyword in c.lower() for keyword in 
                    ['pred', 'forecast', 'top', 'prob', 'score', 'rank'])]
    
    if pred_columns:
        print(f"\n📌 Tabla '{table_name}' contiene columnas de predicción:")
        for col in pred_columns:
            print(f"   - {col}")
        
        # Mostrar ejemplos recientes
        try:
            query = f"SELECT * FROM {table_name} ORDER BY rowid DESC LIMIT 5"
            df = pd.read_sql_query(query, conn)
            print(f"\n   Últimos 5 registros:")
            print(df.to_string(index=False))
        except Exception as e:
            print(f"   Error al leer datos: {e}")

# 5. Verificar si hay datos de programas futuros (posibles predicciones)
print("\n\n📅 VERIFICANDO PROGRAMAS FUTUROS (CON POSIBLES PREDICCIONES):")
print("-" * 80)
try:
    # Buscar tabla de programas
    programa_tables = [t[0] for t in tables if 'prog' in t[0].lower()]
    for table in programa_tables:
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if 'fecha' in column_names or 'date' in column_names:
            date_col = 'fecha' if 'fecha' in column_names else 'date'
            query = f"""
                SELECT {date_col}, COUNT(*) as total_carreras
                FROM {table}
                WHERE {date_col} >= date('now')
                GROUP BY {date_col}
                ORDER BY {date_col}
                LIMIT 10
            """
            df = pd.read_sql_query(query, conn)
            if not df.empty:
                print(f"\n📍 Tabla '{table}' - Programas futuros:")
                print(df.to_string(index=False))
except Exception as e:
    print(f"Error: {e}")

conn.close()

print("\n\n" + "=" * 80)
print("VERIFICACIÓN COMPLETADA")
print("=" * 80)
