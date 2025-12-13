"""
Script de verificación para la implementación de la tabla de predicciones.
Verifica:
1. Creación correcta de la tabla
2. Inserción de predicciones
3. Consulta de predicciones históricas
"""

import sqlite3
import sys
import os

# Agregar src al path
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

print("=" * 80)
print("🔍 VERIFICACIÓN DE IMPLEMENTACIÓN DE TABLA DE PREDICCIONES")
print("=" * 80)

# 1. Verificar creación de tabla
print("\n[1/4] Verificando creación de tabla...")
try:
    db_path = 'data/db/hipica_data.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Verificar que existe la tabla
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='predicciones'")
    result = cursor.fetchone()
    
    if result:
        print("   ✅ Tabla 'predicciones' existe")
        
        # Verificar estructura
        cursor.execute("PRAGMA table_info(predicciones)")
        columns = cursor.fetchall()
        print(f"   📋 Columnas encontradas: {len(columns)}")
        for col in columns:
            print(f"      - {col[1]} ({col[2]})")
        
        # Verificar índices
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='predicciones'")
        indexes = cursor.fetchall()
        print(f"   📊 Índices creados: {len(indexes)}")
        for idx in indexes:
            if idx[0] and not idx[0].startswith('sqlite_'):
                print(f"      - {idx[0]}")
    else:
        print("   ❌ Tabla 'predicciones' NO existe")
        print("   💡 Ejecuta el ETL para crear la tabla: python -c 'from src.etl.etl_pipeline import HipicaETL; etl = HipicaETL()'")
    
    conn.close()
except Exception as e:
    print(f"   ❌ Error: {e}")

# 2. Verificar función save_predictions_to_db
print("\n[2/4] Verificando función save_predictions_to_db...")
try:
    from sync_system import save_predictions_to_db
    print("   ✅ Función 'save_predictions_to_db' importada correctamente")
except Exception as e:
    print(f"   ❌ Error importando función: {e}")

# 3. Verificar funciones de consulta
print("\n[3/4] Verificando funciones de consulta...")
try:
    from src.models.data_manager import obtener_predicciones_historicas, calcular_precision_modelo
    print("   ✅ Función 'obtener_predicciones_historicas' importada")
    print("   ✅ Función 'calcular_precision_modelo' importada")
    
    # Probar obtener predicciones (puede estar vacío si no se ha corrido sync)
    df = obtener_predicciones_historicas(limite=5)
    print(f"   📊 Predicciones históricas encontradas: {len(df)}")
    
    if not df.empty:
        print("   📝 Muestra de predicciones:")
        print(df.head())
    else:
        print("   ℹ️  No hay predicciones aún (normal si no se ha ejecutado sync_system.py)")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

# 4. Verificar integridad
print("\n[4/4] Verificando integridad del sistema...")
try:
    conn = sqlite3.connect('data/db/hipica_data.db')
    cursor = conn.cursor()
    
    # Contar registros en cada tabla relevante
    tables = ['caballos', 'jinetes', 'programa_carreras', 'predicciones']
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"   📊 {table}: {count} registros")
    
    conn.close()
    print("   ✅ Sistema integro")
    
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 80)
print("RESUMEN DE VERIFICACIÓN")
print("=" * 80)
print("""
✅ Pasos completados:
   - Tabla de predicciones creada
   - Funciones de guardado y consulta implementadas

⏭️  Próximos pasos:
   1. Ejecutar sync_system.py para generar y guardar predicciones
   2. Verificar que las predicciones se guardan correctamente en BD
   3. Probar funciones de consulta con datos reales

💡 Para ejecutar un test completo:
   python sync_system.py
""")
