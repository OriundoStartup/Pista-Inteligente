import sqlite3
import sys
sys.path.append('.')
from src.models.data_manager import obtener_patrones_la_tercera

print("=" * 70)
print("VERIFICACIÓN DE POSICIONES Y PATRONES")
print("=" * 70)

# 1. Verificar posiciones en DB
conn = sqlite3.connect('data/db/hipica_data.db')
cursor = conn.cursor()

print("\n📊 VERIFICANDO POSICIONES DEL 12/12:")
query = """
SELECT 
    car.numero as carrera,
    p.posicion,
    c.nombre as caballo
FROM participaciones p
JOIN carreras car ON p.carrera_id = car.id
JOIN jornadas jor ON car.jornada_id = jor.id
JOIN hipodromos h ON jor.hipodromo_id = h.id
JOIN caballos c ON p.caballo_id = c.id
WHERE jor.fecha = '2025-12-12' 
  AND h.nombre LIKE '%Club Hípico%'
  AND p.posicion IS NOT NULL
  AND p.posicion BETWEEN 1 AND 3
ORDER BY car.numero, p.posicion
LIMIT 20
"""

cursor.execute(query)
results = cursor.fetchall()

if results:
    print(f"✅ Encontradas {len(results)} posiciones del top 3:")
    for carrera, pos, caballo in results:
        print(f"   Carrera {carrera}: {pos}° - {caballo}")
else:
    print("❌ No se encontraron posiciones cargadas")

conn.close()

# 2. Verificar detección de patrones
print("\n\n🔍 VERIFICANDO DETECCIÓN DE PATRONES:")
try:
    patrones = obtener_patrones_la_tercera(hipodromo_filtro='Club Hípico de Santiago')
    
    if patrones:
        print(f"✅ Se detectaron {len(patrones)} patrones:")
        for i, patron in enumerate(patrones[:5], 1):  # Mostrar primeros 5
            print(f"\n   Patrón {i}: {patron['tipo']}")
            print(f"   Repeticiones: {patron['veces']} veces")
            print(f"   Caballos:")
            for det in patron['detalle']:
                print(f"      {det['puesto']}° - #{det['numero']} {det['caballo']}")
    else:
        print("⚠️ No se detectaron patrones repetidos")
        
except Exception as e:
    print(f"❌ Error ejecutando detección de patrones: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
