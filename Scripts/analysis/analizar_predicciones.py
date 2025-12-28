import json
from pathlib import Path
from datetime import datetime

print("=" * 90)
print("📊 ANÁLISIS COMPLETO DEL ALMACENAMIENTO DE PREDICCIONES")
print("=" * 90)

# 1. Revisar el cache JSON
cache_path = Path("data/cache_analisis.json")

if cache_path.exists():
    print(f"\n✅ ARCHIVO DE CACHE ENCONTRADO: {cache_path}")
    print(f"   📏 Tamaño: {cache_path.stat().st_size / 1024:.2f} KB")
    print(f"   📅 Última modificación: {datetime.fromtimestamp(cache_path.stat().st_mtime)}")
    
    # Cargar y analizar contenido
    with open(cache_path, 'r', encoding='utf-8') as f:
        cache_data = json.load(f)
    
    print(f"\n📋 CONTENIDO DEL CACHE:")
    print(f"   Total de carreras con predicciones: {len(cache_data)}")
    
    # Agrupar por fecha
    fechas_dict = {}
    for carrera in cache_data:
        fecha = carrera.get('fecha', 'Sin fecha')
        if fecha not in fechas_dict:
            fechas_dict[fecha] = []
        fechas_dict[fecha].append(carrera)
    
    print(f"\n📅 PREDICCIONES POR FECHA:")
    for fecha in sorted(fechas_dict.keys()):
        carreras = fechas_dict[fecha]
        print(f"\n   📆 {fecha}:")
        print(f"      Total de carreras: {len(carreras)}")
        
        for carrera in carreras[:3]:  # Mostrar solo las primeras 3 carreras
            hipodromo = carrera.get('hipodromo', 'N/A')
            nro_carrera = carrera.get('carrera', 'N/A')
            print(f"      - Carrera {nro_carrera} ({hipodromo})")
            
            predicciones = carrera.get('predicciones', [])
            if predicciones:
                # Mostrar top 3 predicciones
                print(f"         Top 3: ", end="")
                for idx, pred in enumerate(predicciones[:3], 1):
                    if isinstance(pred, dict):
                        numero = pred.get('Nº', 'N/A')
                        caballo = pred.get('Caballo', 'N/A')
                        prob = pred.get('Prob_Ganar', 0)
                        print(f"#{numero} {caballo} ({prob:.1%})", end="  ")
                print()
            else:
                print(f"         ⚠️ Sin predicciones")
        
        if len(carreras) > 3:
            print(f"      ... y {len(carreras) - 3} carreras más")
    
    # Estadísticas generales
    print(f"\n\n📊 ESTADÍSTICAS GENERALES:")
    total_con_predicciones = sum(1 for c in cache_data if c.get('predicciones'))
    total_sin_predicciones = len(cache_data) - total_con_predicciones
    print(f"   ✅ Carreras con predicciones: {total_con_predicciones}")
    print(f"   ⚠️  Carreras sin predicciones: {total_sin_predicciones}")
    
    # Verificar estructura de una predicción
    print(f"\n\n🔍 ESTRUCTURA DE UNA PREDICCIÓN (Ejemplo):")
    for carrera in cache_data:
        if carrera.get('predicciones'):
            print(f"   Fecha: {carrera.get('fecha')}")
            print(f"   Hipódromo: {carrera.get('hipodromo')}")
            print(f"   Carrera: {carrera.get('carrera')}")
            print(f"\n   Ejemplo de predicción:")
            pred_ejemplo = carrera['predicciones'][0]
            for key, value in pred_ejemplo.items():
                print(f"      - {key}: {value}")
            break
    
else:
    print("\n❌ ARCHIVO DE CACHE NO ENCONTRADO")

# 2. Conclusión sobre el almacenamiento
print("\n\n" + "=" * 90)
print("📝 CONCLUSIÓN SOBRE EL ALMACENAMIENTO DE PREDICCIONES")
print("=" * 90)

print("""
🔍 HALLAZGOS:

1. ❌ NO HAY TABLA DE PREDICCIONES EN LA BASE DE DATOS
   - Las predicciones NO se están guardando en SQLite (hipica_data.db)
   - Solo se guardan en la base de datos: programas, resultados, caballos, jinetes, etc.

2. ✅ LAS PREDICCIONES SE GUARDAN EN JSON (CACHE)
   - Archivo: data/cache_analisis.json
   - Este archivo se genera cada vez que se ejecuta sync_system.py
   - Se regenera completamente en cada ejecución (se elimina y recrea)

3. 📊 FLUJO ACTUAL DE PREDICCIONES:
   Step 1: sync_system.py ejecuta el ETL → Carga datos en BD
   Step 2: sync_system.py entrena modelos ML → Guarda modelos en .pkl
   Step 3: sync_system.py llama a precalculate_predictions()
           └─> obtener_analisis_jornada() genera predicciones en memoria
           └─> Guarda todo en data/cache_analisis.json
   Step 4: La aplicación web lee de cache_analisis.json para mostrar predicciones

4. ⚠️  VENTAJAS Y DESVENTAJAS:

   VENTAJAS:
   ✅ Las predicciones se generan rápido al leer del cache
   ✅ No se sobrecarga la BD con datos de predicciones que cambian frecuentemente
   
   DESVENTAJAS:
   ❌ No hay historial de predicciones anteriores
   ❌ Si el archivo JSON se pierde, se pierden todas las predicciones
   ❌ No se puede consultar con SQL las predicciones históricas
   ❌ No se puede analizar la precisión del modelo comparando predicciones pasadas

5. 💡 RECOMENDACIÓN:
   
   Si quieres tener un historial de predicciones en la base de datos, deberías:
   
   a) Crear una nueva tabla 'predicciones' en la BD:
      - id, fecha, hipodromo, nro_carrera, numero_caballo, 
        probabilidad_ganar, ranking_prediccion, timestamp_generacion
   
   b) Modificar sync_system.py para guardar las predicciones tanto en:
      - Cache JSON (para lectura rápida de la web)
      - Tabla de BD (para historial y análisis)
   
   c) Esto permitiría:
      - Auditar predicciones históricas
      - Calcular métricas de precisión del modelo
      - Analizar tendencias de predicción
""")

print("\n" + "=" * 90)
print("FIN DEL ANÁLISIS")
print("=" * 90)
