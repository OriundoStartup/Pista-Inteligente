"""
Script de auditoría completa del sistema
Verifica integridad de datos, lógica de fechas y funcionalidad general
"""
import sys
sys.path.append('.')

import sqlite3
import pandas as pd
from datetime import datetime
from pathlib import Path

print("=" * 80)
print("AUDITORÍA COMPLETA DEL SISTEMA - PISTA INTELIGENTE")
print("=" * 80)

# Conectar a BD
db_path = 'data/db/hipica_data.db'
conn = sqlite3.connect(db_path)

# ==========================================
# 1. VERIFICACIÓN DE TABLAS Y REGISTROS
# ==========================================
print("\n[1] VERIFICACIÓN DE TABLAS Y REGISTROS")
print("-" * 80)

tablas = {
    'archivos_procesados': 'Archivos CSV procesados',
    'hipodromos': 'Hipódromos',
    'caballos': 'Caballos',
    'jinetes': 'Jinetes',
    'studs': 'Studs',
    'jornadas': 'Jornadas',
    'carreras': 'Carreras',
    'participaciones': 'Participaciones (resultados)',
    'programa_carreras': 'Programas futuros',
    'predicciones': 'Predicciones IA'
}

for tabla, descripcion in tablas.items():
    try:
        count = pd.read_sql_query(f"SELECT COUNT(*) as total FROM {tabla}", conn)
        print(f"✅ {descripcion:30} {count['total'][0]:6} registros")
    except Exception as e:
        print(f"❌ {descripcion:30} ERROR: {e}")

# ==========================================
# 2. VERIFICACIÓN DE FECHAS
# ==========================================
print("\n[2] VERIFICACIÓN DE FECHAS DISPONIBLES")
print("-" * 80)

# Fechas en jornadas (resultados)
fechas_jornadas = pd.read_sql_query("""
    SELECT DISTINCT fecha, COUNT(*) as carreras
    FROM jornadas j
    JOIN carreras c ON c.jornada_id = j.id
    GROUP BY fecha
    ORDER BY fecha DESC
    LIMIT 10
""", conn)
print("\n📅 Últimas jornadas con resultados:")
print(fechas_jornadas.to_string(index=False))

# Fechas en programas (futuras)
fechas_programas = pd.read_sql_query("""
    SELECT DISTINCT fecha, COUNT(DISTINCT nro_carrera) as carreras
    FROM programa_carreras
    GROUP BY fecha
    ORDER BY fecha DESC
    LIMIT 10
""", conn)
print("\n📅 Fechas en programas:")
print(fechas_programas.to_string(index=False))

# Fecha más reciente vs hoy
hoy = datetime.now().strftime('%Y-%m-%d')
fecha_max_programa = fechas_programas['fecha'].iloc[0] if len(fechas_programas) > 0 else 'N/A'
print(f"\n📆 Hoy: {hoy}")
print(f"📆 Programa más reciente: {fecha_max_programa}")
print(f"✅ Programas son futuras: {fecha_max_programa >= hoy if fecha_max_programa != 'N/A' else 'N/A'}")

# ==========================================
# 3. VERIFICACIÓN DE DUPLICADOS
# ==========================================
print("\n[3] VERIFICACIÓN DE DUPLICADOS")
print("-" * 80)

# Duplicados en participaciones
duplicados_part = pd.read_sql_query("""
    SELECT carrera_id, caballo_id, COUNT(*) as veces
    FROM participaciones
    GROUP BY carrera_id, caballo_id
    HAVING COUNT(*) > 1
""", conn)
print(f"\n🔍 Duplicados en participaciones: {len(duplicados_part)}")
if len(duplicados_part) > 0:
    print(duplicados_part.head(10).to_string(index=False))

# Duplicados en programa
duplicados_prog = pd.read_sql_query("""
    SELECT fecha, hipodromo, nro_carrera, numero, COUNT(*) as veces
    FROM programa_carreras
    GROUP BY fecha, hipodromo, nro_carrera, numero
    HAVING COUNT(*) > 1
""", conn)
print(f"\n🔍 Duplicados en programa: {len(duplicados_prog)}")
if len(duplicados_prog) > 0:
    print(duplicados_prog.head(10).to_string(index=False))

# ==========================================
# 4. VERIFICACIÓN DE ARCHIVOS PROCESADOS
# ==========================================
print("\n[4] ARCHIVOS CSV PROCESADOS")
print("-" * 80)

archivos = pd.read_sql_query("""
    SELECT nombre_archivo, fecha_procesamiento, num_registros
    FROM archivos_procesados
    ORDER BY fecha_procesamiento DESC
""", conn)
print(archivos.to_string(index=False))

# Verificar vs archivos en disco
archivos_disco = list(Path('exports').glob('*.csv'))
archivos_bd = set(archivos['nombre_archivo'].tolist())
archivos_disco_nombres = set(f.name for f in archivos_disco)

print(f"\n📂 Archivos en disco: {len(archivos_disco_nombres)}")
print(f"💾 Archivos procesados: {len(archivos_bd)}")

no_procesados = archivos_disco_nombres - archivos_bd
if no_procesados:
    print(f"⚠️ Archivos NO procesados: {no_procesados}")
else:
    print("✅ Todos los archivos en disco fueron procesados")

# ==========================================
# 5. VERIFICACIÓN DE RELACIONES
# ==========================================
print("\n[5] VERIFICACIÓN DE INTEGRIDAD REFERENCIAL")
print("-" * 80)

# Participaciones sin caballo
sin_caballo = pd.read_sql_query("""
    SELECT COUNT(*) as total
    FROM participaciones
    WHERE caballo_id IS NULL
""", conn)
print(f"🐎 Participaciones sin caballo: {sin_caballo['total'][0]}")

# Programas sin caballo
prog_sin_caballo = pd.read_sql_query("""
    SELECT COUNT(*) as total
    FROM programa_carreras
    WHERE caballo_id IS NULL
""", conn)
print(f"📋 Programas sin caballo: {prog_sin_caballo['total'][0]}")

# Carreras sin participaciones
carreras_vacias = pd.read_sql_query("""
    SELECT COUNT(*) as total
    FROM carreras c
    LEFT JOIN participaciones p ON p.carrera_id = c.id
    WHERE p.id IS NULL
""", conn)
print(f"🏁 Carreras sin participaciones: {carreras_vacias['total'][0]}")

conn.close()

# ==========================================
# 6. VERIFICACIÓN DE MÉTODOS
# ==========================================
print("\n[6] VERIFICACIÓN DE MÉTODOS DE DATA_MANAGER")
print("-" * 80)

from src.models.data_manager import obtener_analisis_jornada, obtener_estadisticas_generales

print("\n🔄 Probando obtener_analisis_jornada...")
try:
    analisis = obtener_analisis_jornada()
    print(f"✅ Análisis generado: {len(analisis)} carreras")
    if len(analisis) > 0:
        fechas = set(c.get('fecha') for c in analisis)
        print(f"📅 Fechas en análisis: {sorted(fechas)}")
        fecha_min = min(fechas) if fechas else 'N/A'
        print(f"✅ Fecha mínima >= hoy: {fecha_min >= hoy if fecha_min != 'N/A' else 'N/A'}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n📊 Probando obtener_estadisticas_generales...")
try:
    stats = obtener_estadisticas_generales()
    print(f"✅ Estadísticas generadas")
    print(f"  • Total carreras: {stats.get('total_carreras', 0)}")
    print(f"  • Top caballos: {len(stats.get('caballos', []))}")
    print(f"  • Top jinetes: {len(stats.get('jinetes', []))}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 80)
print("✅ AUDITORÍA COMPLETADA")
print("=" * 80)
