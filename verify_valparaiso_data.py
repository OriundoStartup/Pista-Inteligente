"""Script to verify Valparaíso data quality in Supabase"""
import os
import sys
from collections import defaultdict
from datetime import datetime, timedelta

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from src.utils.supabase_client import SupabaseManager

def verify_valparaiso_data():
    """Verify Valparaíso data for duplicates and issues"""
    
    print("="*80)
    print("🔍 VERIFICACIÓN DE DATOS DE VALPARAÍSO SPORTING")
    print("="*80)
    
    client = SupabaseManager()
    if not client.get_client():
        print("❌ No se pudo conectar a Supabase")
        return
    
    # 1. Get Valparaíso hippodrome
    print("\n1️⃣ IDENTIFICANDO HIPÓDROMO VALPARAÍSO:")
    try:
        hip_res = client.get_client().table('hipodromos').select('id, nombre').execute()
        valpo_hips = [h for h in hip_res.data if 'Valparaíso' in h['nombre'] or 'Valparaiso' in h['nombre']]
        
        if not valpo_hips:
            print("❌ No se encontró hipódromo de Valparaíso")
            return
        
        valpo_id = valpo_hips[0]['id']
        valpo_name = valpo_hips[0]['nombre']
        print(f"✅ Encontrado: {valpo_name} (ID: {valpo_id})")
        
    except Exception as e:
        print(f"❌ Error consultando hipódromos: {e}")
        return
    
    # 2. Check jornadas for duplicates
    print(f"\n2️⃣ VERIFICANDO JORNADAS DE VALPARAÍSO:")
    try:
        today = datetime.now().date()
        future_date = today - timedelta(days=30)
        
        jorn_res = client.get_client().table('jornadas')\
            .select('id, fecha')\
            .eq('hipodromo_id', valpo_id)\
            .gte('fecha', str(future_date))\
            .order('fecha', desc=True)\
            .execute()
        
        jornadas = jorn_res.data
        print(f"Total jornadas (últimos 30 días): {len(jornadas)}")
        
        # Check for duplicate dates
        fechas_count = defaultdict(list)
        for j in jornadas:
            fechas_count[j['fecha']].append(j['id'])
        
        duplicadas = {f: ids for f, ids in fechas_count.items() if len(ids) > 1}
        if duplicadas:
            print(f"🚨 ENCONTRADAS {len(duplicadas)} FECHAS CON JORNADAS DUPLICADAS:")
            for fecha, ids in sorted(duplicadas.items(), reverse=True):
                print(f"  • Fecha: {fecha}, IDs: {ids}")
        else:
            print("✅ No hay jornadas duplicadas")
        
        # Show future jornadas
        future_jornadas = [j for j in jornadas if j['fecha'] >= str(today)]
        print(f"\n   Jornadas futuras/hoy: {len(future_jornadas)}")
        for j in future_jornadas[:5]:
            print(f"   • {j['fecha']} (ID: {j['id']})")
            
    except Exception as e:
        print(f"❌ Error consultando jornadas: {e}")
        return
    
    # 3. Check carreras for duplicates and invalid data
    print(f"\n3️⃣ VERIFICANDO CARRERAS:")
    try:
        # Get all jornada IDs
        jornada_ids = [j['id'] for j in jornadas]
        
        car_res = client.get_client().table('carreras')\
            .select('id, numero, jornada_id')\
            .in_('jornada_id', jornada_ids)\
            .order('jornada_id')\
            .order('numero')\
            .execute()
        
        carreras = car_res.data
        print(f"Total carreras: {len(carreras)}")
        
        # Check for invalid race numbers
        invalid_races = [c for c in carreras if c['numero'] <= 0]
        if invalid_races:
            print(f"🚨 ENCONTRADAS {len(invalid_races)} CARRERAS CON NÚMERO INVÁLIDO:")
            for c in invalid_races[:5]:
                print(f"  • Carrera ID: {c['id']}, Número: {c['numero']}")
        else:
            print("✅ No hay carreras con números inválidos")
        
        # Check for duplicate race numbers within same jornada
        duplicados_por_jornada = 0
        for jornada in jornadas[:10]:
            jorn_id = jornada['id']
            jorn_carreras = [c for c in carreras if c['jornada_id'] == jorn_id]
            
            numeros_count = defaultdict(list)
            for c in jorn_carreras:
                numeros_count[c['numero']].append(c['id'])
            
            duplicados_num = {n: ids for n, ids in numeros_count.items() if len(ids) > 1}
            if duplicados_num:
                duplicados_por_jornada += 1
                print(f"🚨 Jornada {jornada['fecha']} (ID: {jorn_id}) tiene duplicados:")
                for num, ids in sorted(duplicados_num.items()):
                    print(f"  • Carrera #{num}: {len(ids)} veces (IDs: {ids})")
        
        if duplicados_por_jornada == 0:
            print("✅ No hay carreras duplicadas por jornada")
            
    except Exception as e:
        print(f"❌ Error consultando carreras: {e}")
        return
    
    # 4. Check rendimiento_historico for duplicates
    print(f"\n4️⃣ VERIFICANDO RENDIMIENTO HISTÓRICO:")
    try:
        rend_res = client.get_client().table('rendimiento_historico')\
            .select('fecha, hipodromo, nro_carrera')\
            .eq('hipodromo', valpo_name)\
            .gte('fecha', '2026-01-01')\
            .order('fecha', desc=True)\
            .execute()
        
        rendimientos = rend_res.data
        print(f"Total registros de rendimiento 2026: {len(rendimientos)}")
        
        # Check for duplicates
        race_keys = defaultdict(int)
        for r in rendimientos:
            key = f"{r['fecha']}-{r['nro_carrera']}"
            race_keys[key] += 1
        
        duplicados_rend = {k: count for k, count in race_keys.items() if count > 1}
        if duplicados_rend:
            print(f"🚨 ENCONTRADOS {len(duplicados_rend)} REGISTROS DUPLICADOS:")
            for key, count in sorted(duplicados_rend.items(), reverse=True)[:5]:
                print(f"  • {key}: {count} veces")
        else:
            print("✅ No hay duplicados en rendimiento_historico")
            
    except Exception as e:
        print(f"❌ Error consultando rendimiento: {e}")
    
    # 5. Check predictions for future races
    print(f"\n5️⃣ VERIFICANDO PREDICCIONES FUTURAS:")
    try:
        # Get future jornadas
        future_jornadas = [j for j in jornadas if j['fecha'] >= str(today)]
        if not future_jornadas:
            print("⚠️ No hay jornadas futuras de Valparaíso")
        else:
            future_jornada_ids = [j['id'] for j in future_jornadas]
            
            # Get carreras for future jornadas
            future_car_res = client.get_client().table('carreras')\
                .select('id, numero')\
                .in_('jornada_id', future_jornada_ids)\
                .execute()
            
            future_carreras = future_car_res.data
            print(f"Carreras futuras: {len(future_carreras)}")
            
            if future_carreras:
                future_carrera_ids = [c['id'] for c in future_carreras]
                
                # Get predictions
                pred_res = client.get_client().table('predicciones')\
                    .select('carrera_id, caballo, numero_caballo')\
                    .in_('carrera_id', future_carrera_ids)\
                    .execute()
                
                predicciones = pred_res.data
                print(f"Predicciones futuras: {len(predicciones)}")
                
                if predicciones:
                    # Check for dummy predictions
                    dummy_preds = [p for p in predicciones if p['caballo'] == 'Datos pendientes' or p['caballo'] == 'N/A']
                    if dummy_preds:
                        print(f"⚠️ Encontradas {len(dummy_preds)} predicciones dummy")
                    else:
                        print("✅ Todas las predicciones tienen datos válidos")
                else:
                    print("⚠️ No hay predicciones para carreras futuras")
    except Exception as e:
        print(f"❌ Error consultando predicciones: {e}")
    
    print("\n" + "="*80)
    print("✅ VERIFICACIÓN COMPLETADA")
    print("="*80)

if __name__ == "__main__":
    verify_valparaiso_data()
