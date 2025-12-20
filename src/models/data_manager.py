import sqlite3
import pandas as pd
import itertools
import functools

import os
import json
import joblib
import numpy as np
from datetime import datetime, timedelta
from .features import FeatureEngineering

def cargar_datos(nombre_db='data/db/hipica_data.db'):
    """Carga los datos desde la base de datos SQLite (tabla antigua para compatibilidad)."""
    # Fix paths if running from root or src
    if not os.path.exists(nombre_db) and os.path.exists(f'data/db/{nombre_db}'):
        nombre_db = f'data/db/{nombre_db}'
        
    if not os.path.exists(nombre_db):
        return pd.DataFrame()
        
    try:
        conn = sqlite3.connect(nombre_db)
        df = pd.read_sql("SELECT * FROM resultados", conn)
        conn.close()
        return df
    except Exception as e:
        return pd.DataFrame()

def cargar_datos_3nf(nombre_db='data/db/hipica_data.db'):
    """Carga datos desde la estructura 3NF normalizada."""
    if not os.path.exists(nombre_db) and os.path.exists(f'data/db/{nombre_db}'):
        nombre_db = f'data/db/{nombre_db}'
        
    if not os.path.exists(nombre_db):
        return pd.DataFrame()
    
    try:
        conn = sqlite3.connect(nombre_db)
        query = '''
        SELECT 
            p.id as part_id,
            p.posicion,
            p.mandil,
            p.peso_fs,
            p.dividendo,
            p.tiempo,
            c.id as caballo_id,
            c.nombre as caballo,
            c.ano_nacimiento,
            c.padre,
            j.id as jinete_id,
            j.nombre as jinete,
            jor.fecha,
            h.id as hipodromo_id,
            h.nombre as hipodromo,
            car.distancia,
            car.tipo,
            car.pista,
            car.numero as nro_carrera
        FROM participaciones p
        JOIN carreras car ON p.carrera_id = car.id
        JOIN jornadas jor ON car.jornada_id = jor.id
        JOIN hipodromos h ON jor.hipodromo_id = h.id
        JOIN caballos c ON p.caballo_id = c.id
        JOIN jinetes j ON p.jinete_id = j.id
        ORDER BY jor.fecha DESC, car.numero ASC
        '''
        df = pd.read_sql(query, conn)
        conn.close()
        
        # Limpieza de tipos de datos
        if not df.empty:
            if 'dividendo' in df.columns:
                df['dividendo'] = df['dividendo'].astype(str).str.replace(',', '.', regex=False)
                df['dividendo'] = pd.to_numeric(df['dividendo'], errors='coerce')
            
            if 'peso_fs' in df.columns:
                df['peso_fs'] = df['peso_fs'].astype(str).str.replace('Kg', '', case=False, regex=False).str.strip()
                df['peso_fs'] = pd.to_numeric(df['peso_fs'], errors='coerce')
                
        return df
    except Exception as e:
        print(f"Error cargando datos 3NF: {e}")
        return pd.DataFrame()

def cargar_programa(nombre_db='data/db/hipica_data.db', solo_futuras=True):
    """
    Carga el programa de carreras desde la base de datos.
    
    Args:
        nombre_db: Ruta a la base de datos.
        solo_futuras: Si es True, filtra por fecha >= hoy (optimización de memoria).
    """
    if not os.path.exists(nombre_db) and os.path.exists(f'data/db/{nombre_db}'):
        nombre_db = f'data/db/{nombre_db}'
        
    try:
        conn = sqlite3.connect(nombre_db)
        
        # Filtro de fecha inyectable
        fecha_filter = ""
        if solo_futuras:
            # FIX: Use Python to determine date, avoiding SQLite 'localtime' issues on Cloud Run (UTC)
            # Chile is UTC-3 (approx, ignoring DST complex rules for now or use pytz if available)
            from datetime import timedelta
            
            # Simple offset -3 hours for Chile
            # A more robust solution uses pytz, but basic offset covers 99% of cases for "Today"
            chile_time = datetime.utcnow() - timedelta(hours=3)
            today_str = chile_time.strftime('%Y-%m-%d')
            
            fecha_filter = f"WHERE pc.fecha >= '{today_str}'"

        # Try to join with normalized tables if they exist, otherwise raw
        try:
             # Normalized programmatic join
             query = f"""
                SELECT 
                    pc.fecha, h.nombre as hipodromo, pc.nro_carrera, pc.hora, pc.distancia, pc.condicion,
                    pc.numero as numero, 
                    COALESCE(c.nombre, 'Desconocido') as caballo, 
                    j.nombre as jinete, 
                    s.nombre as stud, 
                    pc.peso
                FROM programa_carreras pc
                LEFT JOIN hipodromos h ON pc.hipodromo = h.nombre OR h.codigo = pc.hipodromo
                LEFT JOIN caballos c ON pc.caballo_id = c.id
                LEFT JOIN jinetes j ON pc.jinete_id = j.id
                LEFT JOIN studs s ON pc.stud_id = s.id
                {fecha_filter}
                ORDER BY pc.fecha ASC, pc.nro_carrera ASC, pc.numero ASC
             """
             df = pd.read_sql(query, conn)
        except:
             # Fallback to simple select if flat table
             # También aplicamos filtro si es posible
             where_simple = f"WHERE fecha >= '{today_str}'" if solo_futuras else ""
             df = pd.read_sql(f"SELECT * FROM programa_carreras {where_simple}", conn)
             
        conn.close()
        return df
    except Exception as e:
        print(f"Error cargando programa: {e}")
        return pd.DataFrame()

# Global variable for in-memory cache to replace lru_cache
_memory_cache = {
    'data': None,
    'mtime': 0,
    'path': None
}

def obtener_analisis_jornada():
    """Genera análisis usando ML o carga desde cache con validación de frescura."""
    # --- CACHE LOGIC START ---
    from pathlib import Path
    import json
    
    # Intentar cargar desde cache
    try:
        # Ajustamos path para que funcione tanto local como en container
        cache_path = Path("data/cache_analisis.json")
        if not cache_path.exists():
             cache_path = Path("app/data/cache_analisis.json")

        if cache_path.exists():
            current_mtime = cache_path.stat().st_mtime
            
            # Check if we have valid memory cache
            if _memory_cache['data'] is not None and \
               _memory_cache['path'] == str(cache_path) and \
               _memory_cache['mtime'] == current_mtime:
                return _memory_cache['data']

            # If not in memory or file changed, reload from disk
            with open(cache_path, 'r', encoding='utf-8') as f:
                print(f"⚡ [DISK] Recargando cache predicciones ({current_mtime})")
                data = json.load(f)
                
                # FIX: Normalizar nombres de hipódromos 'legacy' o 'raw' al vuelo
                # Esto corrige VALP/VAL -> Valparaíso Sporting inmediatamente en la vista
                for carrera in data:
                    hip = carrera.get('hipodromo', '')
                    if hip == 'VALP' or hip == 'VAL':
                        carrera['hipodromo'] = 'Valparaíso Sporting'
                
                # Update memory cache
                _memory_cache['data'] = data
                _memory_cache['mtime'] = current_mtime
                _memory_cache['path'] = str(cache_path)
                
                return data
    except Exception as e:
        print(f"⚠️ Error al leer cache, calculando dinámicamente: {e}")
        # Invalidate memory cache on error
        _memory_cache['data'] = None
    # --- CACHE LOGIC END ---

    print("🔄 Calculando predicciones dinámicamente...")
    # Cargar programa (ya filtrado >= hoy por defecto)
    df_programa = cargar_programa(solo_futuras=True)
    
    if df_programa.empty:
        return []
        
    analisis_completo = []
    
    # Cargar modelo ML v3 + Features
    model = None
    fe = None
    try:
        model = joblib.load('src/models/gb_model_v3.pkl')
        fe = FeatureEngineering.load('src/models/feature_eng_v2.pkl')
        ml_available = True
    except:
        ml_available = False
    
    # Cargar datos históricos para features
    df_historial = cargar_datos_3nf()
    
    if not df_programa.empty:
        if 'fecha' in df_programa.columns:
            df_programa['fecha_dt'] = pd.to_datetime(df_programa['fecha'])
            # Filtrar para mostrar programas desde hoy en adelante
            if not df_programa.empty:
                # today = datetime.now().strftime('%Y-%m-%d')
                # future_programs = df_programa[df_programa['fecha'] >= today]
                # Para permitir calcular precisión histórica, procesamos todo
                future_programs = df_programa
                
                if not future_programs.empty:
                    df_programa = future_programs
                else:
                    # Si no hay futuros, mostrar el último disponible (fallback)
                    latest_date = df_programa['fecha_dt'].max()
                    df_programa = df_programa[df_programa['fecha_dt'] == latest_date]

            
    if 'numero' in df_programa.columns and not df_programa.empty:
        # Assuming 'nro_carrera' exists or 'carrera' column
        carrera_col = 'nro_carrera' if 'nro_carrera' in df_programa.columns else 'carrera'
        
        grupos = df_programa.groupby(['fecha', 'hipodromo', carrera_col])
        
        for (fecha, hipodromo, nro_carrera), grupo in grupos:
            caballos_df = grupo[['numero', 'caballo', 'jinete', 'stud', 'peso']].copy()
            caballos_df['numero'] = pd.to_numeric(caballos_df['numero'], errors='coerce').fillna(0).astype(int)
            caballos_df = caballos_df.sort_values('numero').reset_index(drop=True)
            
            # Extract context for ML
            distancia_val = grupo.iloc[0]['distancia'] 
            try:
                distancia_val = float(str(distancia_val).replace('.','')) if isinstance(distancia_val, str) else float(distancia_val)
            except:
                distancia_val = 1100.0

            fecha_val = grupo.iloc[0]['fecha']
            pista_val = grupo.iloc[0].get('condicion', 'ARENA')
            
            # Context dict
            ctx = {
                'distancia': distancia_val,
                'fecha': fecha_val,
                'pista': pista_val,
                'hipodromo': hipodromo
            }

            if ml_available and not df_historial.empty:
                predicciones = analizar_probabilidad_caballos(caballos_df, df_historial, model=model, fe=fe, context=ctx)
            else:
                predicciones = analizar_probabilidad_caballos(caballos_df, df_historial, model=None, fe=None, context=ctx)
            
            caballos_df.columns = ['Nº', 'Caballo', 'Jinete', 'Stud', 'Peso']
            
            analisis_completo.append({
                'hipodromo': hipodromo,
                'carrera': nro_carrera,
                'fecha': fecha,
                'hora': grupo.iloc[0]['hora'],
                'distancia': grupo.iloc[0]['distancia'],
                'caballos': caballos_df,
                'predicciones': predicciones
            })
    
    analisis_completo.sort(key=lambda x: (x['fecha'], x['hipodromo'], x['carrera']))
    return analisis_completo

def analizar_probabilidad_caballos(caballos_df, historial_resultados, model=None, fe=None, context=None):
    """Analiza probabilidades usando ML + Heurística híbrida."""
    if historial_resultados.empty or caballos_df.empty:
        return []

    predicciones = []
    
    # Context
    distancia = context.get('distancia', 1000) if context else 1000
    fecha_carrera = pd.to_datetime(context.get('fecha', datetime.now())) if context else datetime.now()
    pista = context.get('pista', 'ARENA') if context else 'ARENA'
    
    scores = []
    
    for idx, row in caballos_df.iterrows():
        nombre = row.get('caballo', '').strip()
        val_num = row.get('numero', 0)
        jinete_nombre = row.get('jinete', 'Jinete')
        peso_val = row.get('peso', 470)
        
        # Heuristic Score (legacy fallback/hybrid factor)
        heuristic_score = 50.0
        
        # Robust Name Matching
        caballo_hist = historial_resultados[historial_resultados['caballo'] == nombre].sort_values('fecha')
        
        # Fallback: Try match without extra spaces if exact fails
        if caballo_hist.empty:
             caballo_hist = historial_resultados[historial_resultados['caballo'].str.strip() == nombre].sort_values('fecha')

        if not caballo_hist.empty:
            # Simple stats for legacy score
            wins = len(caballo_hist[caballo_hist['posicion'] == 1])
            runs = len(caballo_hist)
            win_rate = wins / runs if runs > 0 else 0
            heuristic_score += (win_rate * 50.0) 
            
            # Recency bonus
            try:
                last_run = pd.to_datetime(caballo_hist.iloc[-1]['fecha'])
                days_since = (fecha_carrera - last_run).days
                if days_since < 30: heuristic_score += 5
            except: pass
        else:
            heuristic_score = 45.0 # Debutante
            print(f"   ⚠️ Debutante o Sin Historia: {nombre}")

        # ML Prep
        ml_score = 50.0
        if model and fe:
            try:
                # Find Jinete ID
                j_id = 0
                j_hist = historial_resultados[historial_resultados['jinete'] == jinete_nombre]
                if not j_hist.empty:
                    j_id = j_hist.iloc[0]['jinete_id']
                
                c_id = 0
                if not caballo_hist.empty:
                    c_id = caballo_hist.iloc[0]['caballo_id']

                # Create the "Current" row
                current_row = {
                    'fecha': fecha_carrera,
                    'caballo_id': c_id,
                    'jinete_id': j_id,
                    'distancia': distancia,
                    'pista': pista,
                    'peso_fs': peso_val,
                    'mandil': val_num,
                    'tiempo': 0, 
                    'posicion': 0, 
                    'is_win': 0 
                }
                
                cols_needed = ['fecha', 'caballo_id', 'jinete_id', 'distancia', 'pista', 'peso_fs', 'mandil', 'tiempo', 'posicion']
                
                # Combine history + current
                if caballo_hist.empty:
                     h_subset = pd.DataFrame([current_row]) 
                else:
                     h_subset = pd.concat([caballo_hist[cols_needed].copy(), pd.DataFrame([current_row])], ignore_index=True)
                
                feats = fe.transform(h_subset, is_training=False)
                last_feat = feats.iloc[-1:].copy()
                
                # Predict
                prob = model.predict_proba(last_feat)[0][1]
                ml_score = prob * 100
                
            except Exception as e:
                ml_score = 50.0 

        # Hybrid Score
        final_score = (heuristic_score * 0.4) + (ml_score * 0.6)
        
        scores.append({
            'numero': int(val_num),
            'caballo': nombre,
            'jinete': jinete_nombre,
            'raw_score': final_score,
            'ml_prob': ml_score
        })
        
    # Relative Normalization
    if not scores: return []
    
    max_score = max(s['raw_score'] for s in scores)
    min_score = min(s['raw_score'] for s in scores)
    
    if max_score == min_score:
        for s in scores:
             s['puntaje_ia'] = 85.0
             s['prob_ml'] = "50.0"
    else:
        for s in scores:
            normalized = 60 + ((s['raw_score'] - min_score) / (max_score - min_score)) * (99 - 60)
            s['puntaje_ia'] = round(normalized, 1)
            s['prob_ml'] = f"{s['ml_prob']:.1f}"

    scores.sort(key=lambda x: x['puntaje_ia'], reverse=True)
    
    return [{
        'numero': s['numero'],
        'caballo': s['caballo'],
        'jinete': s['jinete'],
        'puntaje_ia': s['puntaje_ia'],
        'prob_ml': s['prob_ml']
    } for s in scores[:4]]

def obtener_lista_hipodromos():
    """Obtiene la lista única de hipódromos."""
    try:
        df = cargar_datos_3nf()
        if df.empty:
             df = cargar_datos()
             
        if not df.empty and 'hipodromo' in df.columns:
            # Normalize VALP/VAL -> Valparaíso Sporting before list generation
            # This ensures they don't appear as separate entries in filter buttons
            raw_list = df['hipodromo'].unique().tolist()
            normalized = set()
            for h in raw_list:
                if h in ['VALP', 'VAL']:
                    normalized.add('Valparaíso Sporting')
                elif h == 'VSC':
                     normalized.add('Valparaíso Sporting') # Map VSC too just in case
                else:
                    normalized.add(h)
            
            return sorted(list(normalized))
        return []
    except:
        return []

def calcular_todos_patrones(df=None):
    """
    Calcula TODOS los patrones para todo el historial disponible.
    Retorna una lista de patrones completa (sin filtrar por hipódromo aún).
    """
    if df is None:
        df = cargar_datos_3nf()
    
    if df.empty: return []

    # Agrupar por carrera
    try:
        carreras_groups = df.groupby(['hipodromo', 'fecha', 'nro_carrera'])
    except KeyError:
        # Fallback si faltan columnas
        return []

    # Contadores Globales
    # Key: (Signature, Hipodromo) -> Count
    # We include Hipodromo in key to ensure we don't mix generic patterns if user wants specificity,
    # BUT "Pattern" usually means "Same horse names win anywhere". 
    # The requirement seems to be "Resultados Repetidos" (Same horses).
    # If Horse A and Horse B make a Quinela in Hipodromo Chile, and later in Club Hipico, 
    # is that a repetition? YES. It shows they run well together.
    # So we count GLOBALLY.
    
    quinelas = {}
    trifectas = {}
    superfectas = {}
    
    # Init details map: Signature -> List of occurences (details)
    details_map = {} 

    for (hip, fecha, nro), grupo in carreras_groups:
        # Ordenar por llegada
        llegada = grupo.sort_values('posicion')
        top4 = llegada.head(4)
        
        if len(top4) < 2: continue
        
        # Extract data
        caballos = top4['caballo'].tolist()
        
        # Details for this race
        race_details = top4.to_dict('records')
        # Add metadata for filtering later in view
        for r in race_details:
            r['hipodromo'] = hip
            r['fecha'] = fecha
            r['nro_carrera'] = nro

        # Quinela (Top 2 - Box allowed in logic, checking sorted tuple)
        sig_quinela = tuple(sorted(caballos[:2])) 
        if len(sig_quinela) == 2:
            quinelas[sig_quinela] = quinelas.get(sig_quinela, 0) + 1
            if sig_quinela not in details_map: details_map[sig_quinela] = []
            details_map[sig_quinela].append(race_details[:2])

        # Trifecta (Top 3)
        if len(top4) >= 3:
            sig_trifecta = tuple(caballos[:3])
            trifectas[sig_trifecta] = trifectas.get(sig_trifecta, 0) + 1
            if sig_trifecta not in details_map: details_map[sig_trifecta] = []
            details_map[sig_trifecta].append(race_details[:3])

        # Superfecta (Top 4)
        if len(top4) >= 4:
            sig_superfecta = tuple(caballos[:4])
            superfectas[sig_superfecta] = superfectas.get(sig_superfecta, 0) + 1
            if sig_superfecta not in details_map: details_map[sig_superfecta] = []
            details_map[sig_superfecta].append(race_details[:4])

    patrones = []

    def pack_patron(signature, count, tipo):
        if count >= 2:
            # Flatten details: The details_map now has a LIST of LISTS of records.
            # We want to show all occurences.
            # Signature matches, so we show the "Last" or "All"?
            # Showing ALL instances of the pattern is best.
            
            all_occurences = details_map.get(signature, [])
            # Flatten nicely
            flat_items = []
            for occurence in all_occurences:
                for r in occurence:
                     flat_items.append({
                        'puesto': int(r['posicion']) if pd.notna(r['posicion']) else 0,
                        'numero': int(r['mandil']) if pd.notna(r['mandil']) else 0,
                        'caballo': r['caballo'],
                        'jinete': r['jinete'],
                        'hipodromo': r.get('hipodromo', ''), # Important for view
                        'fecha': r.get('fecha', '')
                    })
            
            # Remove duplicated entries if multiple people run? No, they are distinct rows.
            # Sorting by date might be nice?
            flat_items.sort(key=lambda x: x['fecha'], reverse=True)

            return {'tipo': tipo, 'veces': count, 'detalle': flat_items, 'signature': signature}
        return None

    for sig, count in quinelas.items():
        p = pack_patron(sig, count, 'Quinela Repetida (2 Aciertos)')
        if p: patrones.append(p)

    for sig, count in trifectas.items():
        p = pack_patron(sig, count, 'Trifecta Repetida (3 Aciertos)')
        if p: patrones.append(p)
        
    for sig, count in superfectas.items():
        p = pack_patron(sig, count, 'Superfecta Repetida (4 Aciertos)')
        if p: patrones.append(p)

    # Sort by count desc
    patrones.sort(key=lambda x: x['veces'], reverse=True)
    return patrones

def obtener_patrones_la_tercera(hipodromo_filtro=None):
    """Busca patrones de resultados repetidos. Usa CACHE JSON si existe."""
    # 1. Try Load from Cache
    import json
    from pathlib import Path
    
    patrones = []
    last_updated = "Reciente"
    loaded_from_cache = False
    
    try: # New outer try block
        try: # Existing cache try block
            cache_path = Path("data/cache_patrones.json")
            if not cache_path.exists():
                 cache_path = Path("app/data/cache_patrones.json")

            if cache_path.exists():
                with open(cache_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Support new format (dict) and legacy (list)
                    if isinstance(data, dict):
                        patrones = data.get('patterns', [])
                        last_updated = data.get('last_updated', 'Reciente')
                    elif isinstance(data, list):
                        patrones = data
                        last_updated = "Reciente (Formato antiguo)"
                        
                    loaded_from_cache = True
                    # print("⚡ Patrones cargados desde cache JSON")
        except Exception as e:
            print(f"⚠️ Error leyendo cache patrones: {e}")

        # 2. If no cache, calculate live (slower but fallback)
        # 2. If no cache, calculate live (slower but fallback)
        if not patrones and not loaded_from_cache:
            try: # Existing dynamic calculation try block
                print("🔄 Calculando patrones dinámicamente...")
                patrones = calcular_todos_patrones()
                last_updated = "Calculado en vivo"
            except Exception as e:
                print(f"❌ Error calculando patrones: {e}")
                patrones = [] # Safety fallback

        # 3. Filter if needed
        if hipodromo_filtro and hipodromo_filtro != 'Todos':
            # Filtering patterns is tricky:
            # A pattern is valid if it happened twice.
            # If I filter by "Hipodromo Chile", do I only show patterns that happened exclusively there?
            # Or do I show patterns where AT LEAST ONE occurence was there?
            # Usually "Filter View" means "Show me things relevant to this track".
            # Let's simple filter: Only show patterns where the LATEST occurence was in this track?
            # Or filtered based on the 'detalle' items?
            
            # Simplest Logic matching previous:
            # The previous logic filtered the DF *before* counting.
            # This implies: "Find patterns that exist within the subset of races at Hipodromo X".
            # (e.g. A and B won together twice AT Club Hipico).
            
            # If we load GLOBAL patterns from cache, we cannot easily retroactive filter to "Local only" counts 
            # without looking at all details.
            
            # Strategy:
            # If cached data is GLOBAL, we scan 'detalle'.
            # We RE-COUNT occurrences that match the hipodromo.
            # If re-count >= 2, we keep it.
            
            filtered_patrones = []
            for p in patrones:
                # Count details matching hipodromo
                relevant_details = [d for d in p['detalle'] if d.get('hipodromo') == hipodromo_filtro]
                
                # Since 'detalle' has multple rows per race (2 for quinela), we need to count unique races.
                # Unique (fecha, nro_carrera) tuples.
                unique_races = set((d['fecha'], d.get('fecha_hora', '')) for d in relevant_details) 
                # Note: detail structure in pack_patron uses 'fecha'.
                unique_races = set(d['fecha'] for d in relevant_details) # Approx check
                
                # Actually, let's just count how many sets of "1st, 2nd" etc we have.
                # Easier: Check metadata.
                # But the cache implementation above stores EVERYTHING.
                
                # Optimization: If the user filters, the pattern MUST consist of events in that hipodromo
                # to be a "Pattern of THAT hipodromo".
                # If standard behavior is "Local Patterns", then Global Cache is only useful if we store sufficient metadata.
                
                # Wait, if `obtener_patrones` was previously filtering DF first, it meant:
                # "Find pairs that repeated WITHIN this hipodromo".
                # Cross-hipodromo patterns were ignored if filter was active.
                
                # If we want to support this with cache:
                # We filter the 'detalle' list to only include entries from 'hipodromo_filtro'.
                # Then we verify if there are still >= 2 distinct races involved.
                
                # Group details by race (fecha)
                races_involved = set()
                local_details = []
                
                for d in p['detalle']:
                    if d.get('hipodromo') == hipodromo_filtro:
                        races_involved.add(d.get('fecha'))
                        local_details.append(d)
                
                if len(races_involved) >= 2:
                    # Create a copy with only local details
                    p_copy = p.copy()
                    p_copy['detalle'] = local_details
                    p_copy['veces'] = len(races_involved)
                    filtered_patrones.append(p_copy)
                    
            patrones = filtered_patrones
            patrones.sort(key=lambda x: x['veces'], reverse=True)

        return patrones, last_updated # Modified return statement
    except Exception as e:
        traceback.print_exc()
        print(f"❌ CRITICAL ERROR in obtener_patrones: {e}")
        return [], "Error de Sistema"

def detectar_patrones_futuros():
    """
    Analiza el programa futuro y busca si algún subconjunto de caballos 
    coincide con patrones históricos (ej. Quinelas repetidas).
    Retorna una lista de 'Alertas de Patrón'.
    """
    try:
        # 1. Obtener programa futuro
        programa = obtener_analisis_jornada()
        if not programa: return []
        
        # 2. Obtener patrones históricos
        patrones, _ = obtener_patrones_la_tercera() # Global patterns
        if not patrones: return []
        
        # Indexar patrones por signature (set for easier subset check)
        # Signature is tuple of names sorted.
        # We focus on Quinelas (len 2) mainly as they are most common repeating unit.
        # Trifectas (len 3) also valid.
        
        relevant_patterns = []
        
        for p in patrones:
            # Solo nos interesan patrones que se han repetido
            if p['veces'] >= 2:
                # Convert signature to set for subset check
                p['sig_set'] = set(p['signature'])
                relevant_patterns.append(p)
        
        alerts = []
        
        for carrera in programa:
            # Caballos en esta carrera futura
            # carrera['caballos'] is a list of dicts or DF. data_manager returns dicts in serializable.
            # But inside data_manager, obtaining directly might be list of dicts if cached, or dict if not.
            # obtener_analisis_jornada checks cache and returns list of dicts.
            
            caballos_carrera = carrera.get('caballos', [])
            # Normalize names
            nombres_carrera = set()
            for c in caballos_carrera:
                name = c.get('Caballo', '') or c.get('caballo', '') # Case sensitive keys check
                if name: nombres_carrera.add(name.strip())
            
            if len(nombres_carrera) < 2: continue

            # Check against patterns
            for p in relevant_patterns:
                sig_set = p['sig_set']
                
                # Check if Pattern is a SUBSET of Race Horses
                # i.e. Are both horses form the Quinela present in this race?
                if sig_set.issubset(nombres_carrera):
                    # MATCH FOUND!
                    alerts.append({
                        'hipodromo': carrera['hipodromo'],
                        'fecha_carrera': carrera['fecha'],
                        'nro_carrera': carrera['carrera'],
                        'tipo_patron': p['tipo'],
                        'veces_previas': p['veces'],
                        'caballos_involucrados': list(p['signature']), # Tuple to list
                        'detalle_previo': p['detalle'] # Full history
                    })
        
        # Sort by relevance (max reps)
        alerts.sort(key=lambda x: x['veces_previas'], reverse=True)
        return alerts

    except Exception as e:
        print(f"Error detectando patrones futuros: {e}")
        import traceback
        traceback.print_exc()
        return []


def obtener_estadisticas_generales():
    """Calcula estadísticas generales de rendimiento."""
    df = cargar_datos_3nf()
    if df.empty:
        return {'jinetes': [], 'caballos': [], 'pistas': [], 'total_carreras': 0, 'aciertos_ultimo_mes': 0, 'dividendos_generados': 0}

    try:
        # 1. Top Jinetes (Por Eficiencia de Ganador)
        # Filtrar jinetes con al menos 5 carreras para evitar sesgos de 100% con 1 carrera
        jinetes_stats = df.groupby('jinete').agg(
            carreras=('posicion', 'count'),
            ganadas=('posicion', lambda x: (x==1).sum()),
            top3=('posicion', lambda x: (x<=3).sum())
        ).reset_index()
        
        jinetes_stats = jinetes_stats[jinetes_stats['carreras'] >= 5]
        jinetes_stats['eficiencia'] = ((jinetes_stats['ganadas'] / jinetes_stats['carreras']) * 100).round(1)
        top_jinetes = jinetes_stats.sort_values('eficiencia', ascending=False).head(10).to_dict('records')
        
        # 2. Top Caballos (Más ganadores recientemente)
        caballos_stats = df.groupby('caballo').agg(
            carreras=('posicion', 'count'),
            ganadas=('posicion', lambda x: (x==1).sum())
        ).reset_index()
        top_caballos = caballos_stats.sort_values('ganadas', ascending=False).head(10).to_dict('records')
        
        # 3. Estadísticas por Pista (Hipódromo)
        pistas_stats = df.groupby('hipodromo').agg(
            carreras=('nro_carrera', 'count'), # Total participaciones
            promedio_div=('dividendo', 'mean')
        ).reset_index()
        pistas_stats['promedio_div'] = pistas_stats['promedio_div'].fillna(0)
        track_stats = pistas_stats.to_dict('records')

        # 4. Precision mes y Dividendos (Usando funcion existente)
        # Calcular ultimos 30 dias
        try:
             fecha_fin = datetime.now()
             fecha_inicio = fecha_fin - timedelta(days=30)
             
             # Formato string YYYY-MM-DD
             f_inicio_str = fecha_inicio.strftime('%Y-%m-%d')
             f_fin_str = fecha_fin.strftime('%Y-%m-%d')
             
             precision_data = calcular_precision_modelo(fecha_inicio=f_inicio_str, fecha_fin=f_fin_str)
             
             aciertos_mes = precision_data.get('top1_accuracy', 0)
             dividendos_generados = precision_data.get('total_dividendos', 0)
        except Exception as e:
             print(f"Error calc precision stats: {e}")
             aciertos_mes = 0
             dividendos_generados = 0
        
        return {
            'jinetes': top_jinetes,
            'caballos': top_caballos,
            'pistas': track_stats,
            'total_carreras': len(df),
            'aciertos_ultimo_mes': float(aciertos_mes),
            'dividendos_generados': round(float(dividendos_generados), 1)
        }
        
    except Exception as e:
        print(f"Error calculando estadisticas: {e}")
        return {'jinetes': [], 'caballos': [], 'pistas': [], 'total_carreras': 0}

def obtener_predicciones_historicas(fecha_inicio=None, fecha_fin=None, hipodromo=None, limite=100, nombre_db='data/db/hipica_data.db'):
    """
    Obtiene predicciones históricas de la base de datos.
    
    Args:
        fecha_inicio: Fecha inicial del filtro (formato 'YYYY-MM-DD')
        fecha_fin: Fecha final del filtro (formato 'YYYY-MM-DD')
        hipodromo: Filtrar por hipódromo específico
        limite: Número máximo de registros a retornar
        nombre_db: Ruta a la base de datos
        
    Returns:
        DataFrame con las predicciones históricas
    """
    if not os.path.exists(nombre_db) and os.path.exists(f'data/db/{nombre_db}'):
        nombre_db = f'data/db/{nombre_db}'
        
    try:
        conn = sqlite3.connect(nombre_db)
        
        query = """
        SELECT 
            p.id,
            p.fecha_generacion,
            p.fecha_carrera,
            p.hipodromo,
            p.nro_carrera,
            p.numero_caballo,
            c.nombre as caballo,
            j.nombre as jinete,
            p.puntaje_ia,
            p.prob_ml,
            p.ranking_prediccion,
            p.metadata
        FROM predicciones p
        LEFT JOIN caballos c ON p.caballo_id = c.id
        LEFT JOIN jinetes j ON p.jinete_id = j.id
        WHERE 1=1
        """
        
        params = []
        
        if fecha_inicio:
            query += " AND p.fecha_carrera >= ?"
            params.append(fecha_inicio)
            
        if fecha_fin:
            query += " AND p.fecha_carrera <= ?"
            params.append(fecha_fin)
            
        if hipodromo:
            query += " AND p.hipodromo = ?"
            params.append(hipodromo)
        
        query += " ORDER BY p.fecha_generacion DESC, p.ranking_prediccion ASC LIMIT ?"
        params.append(limite)
        
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        
        return df
        
    except Exception as e:
        print(f"Error obteniendo predicciones históricas: {e}")
        return pd.DataFrame()

def obtener_ultimos_aciertos(dias=30, nombre_db='data/db/hipica_data.db'):
    """
    Obtiene los aciertos recientes (Ranking 1 que ganó la carrera) de los últimos X días.
    """
    if not os.path.exists(nombre_db) and os.path.exists(f'data/db/{nombre_db}'):
        nombre_db = f'data/db/{nombre_db}'
        
    try:
        conn = sqlite3.connect(nombre_db)
        
        # Calculate date threshold in Python for safety
        fecha_limite = (datetime.now() - timedelta(days=dias)).strftime('%Y-%m-%d')
        
        query = """
        SELECT 
            p.fecha_carrera,
            p.hipodromo,
            p.nro_carrera,
            p.numero_caballo,
            c.nombre as caballo,
            p.puntaje_ia,
            part.dividendo
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
        WHERE jor.fecha = p.fecha_carrera
            AND car.numero = p.nro_carrera
            AND part.posicion = 1 
            AND p.ranking_prediccion = 1
            AND p.fecha_carrera >= ?
        ORDER BY p.fecha_carrera DESC
        """
        
        df = pd.read_sql_query(query, conn, params=(fecha_limite,))
        conn.close()
        
        if not df.empty and 'dividendo' in df.columns:
            df['dividendo'] = df['dividendo'].astype(str).str.replace(',', '.', regex=False)
            df['dividendo'] = pd.to_numeric(df['dividendo'], errors='coerce').fillna(0)
            
        return df.to_dict('records')
        
    except Exception as e:
        print(f"Error obteniendo aciertos: {e}")
        return []

def calcular_precision_modelo(fecha_inicio=None, fecha_fin=None, nombre_db='data/db/hipica_data.db'):
    """
    Calcula métricas de precisión del modelo comparando predicciones con resultados reales.
    
    Args:
        fecha_inicio: Fecha inicial del análisis
        fecha_fin: Fecha final del análisis
        nombre_db: Ruta a la base de datos
        
    Returns:
        Dict con métricas de precisión (Top 1, Top 3, Top 4 accuracy)
    """
    if not os.path.exists(nombre_db) and os.path.exists(f'data/db/{nombre_db}'):
        nombre_db = f'data/db/{nombre_db}'
        
    try:
        conn = sqlite3.connect(nombre_db)
        
        # Query que une predicciones con resultados reales
        query = """
        SELECT 
            p.fecha_carrera,
            p.hipodromo,
            p.nro_carrera,
            p.numero_caballo,
            p.caballo_id,
            p.ranking_prediccion,
            part.posicion as posicion_real,
            part.dividendo as div_real
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
        WHERE jor.fecha = p.fecha_carrera
            AND car.numero = p.nro_carrera
            AND part.posicion IS NOT NULL
        """
        
        params = []
        
        if fecha_inicio:
            query += " AND p.fecha_carrera >= ?"
            params.append(fecha_inicio)
            
        if fecha_fin:
            query += " AND p.fecha_carrera <= ?"
            params.append(fecha_fin)
        
        df = pd.read_sql_query(query, conn, params=params if params else None)
        conn.close()
        
        if df.empty:
            return {
                'total_predicciones': 0,
                'total_carreras': 0,
                'top1_accuracy': 0.0,
                'top3_accuracy': 0.0,
                'top4_accuracy': 0.0,
                'total_dividendos': 0.0,
                'mensaje': 'No hay datos suficientes para calcular precisión'
            }
        
        # Calcular métricas
        total_carreras = df.groupby(['fecha_carrera', 'hipodromo', 'nro_carrera']).ngroups
        
        # Top 1: El caballo con ranking 1 en predicciones terminó en posición 1
        top1_correct = len(df[(df['ranking_prediccion'] == 1) & (df['posicion_real'] == 1)])
        total_top1_predictions = len(df[df['ranking_prediccion'] == 1])
        top1_accuracy = (top1_correct / total_top1_predictions * 100) if total_top1_predictions > 0 else 0
        
        # Dividendos (Solo ganadores que fueron Top 1)
        try:
             hits_df = df[(df['ranking_prediccion'] == 1) & (df['posicion_real'] == 1)].copy()
             # Limpiar dividendo
             if not hits_df.empty:
                 hits_df['div_real'] = hits_df['div_real'].astype(str).str.replace(',', '.', regex=False)
                 hits_df['div_real'] = pd.to_numeric(hits_df['div_real'], errors='coerce').fillna(0)
                 total_dividendos = hits_df['div_real'].sum()
             else:
                 total_dividendos = 0.0
        except Exception as e:
             print(f"Error calc dividendos: {e}")
             total_dividendos = 0.0

        # Top 3: Caballos predichos en top 3 que terminaron en top 3
        top3_correct = len(df[(df['ranking_prediccion'] <= 3) & (df['posicion_real'] <= 3)])
        total_top3_predictions = len(df[df['ranking_prediccion'] <= 3])
        top3_accuracy = (top3_correct / total_top3_predictions * 100) if total_top3_predictions > 0 else 0
        
        # Top 4: Caballos predichos en top 4 que terminaron en top 4
        top4_correct = len(df[(df['ranking_prediccion'] <= 4) & (df['posicion_real'] <= 4)])
        total_top4_predictions = len(df[df['ranking_prediccion'] <= 4])
        top4_accuracy = (top4_correct / total_top4_predictions * 100) if total_top4_predictions > 0 else 0
        
        return {
            'total_predicciones': len(df),
            'total_carreras': total_carreras,
            'top1_accuracy': round(top1_accuracy, 2),
            'top1_correct': top1_correct,
            'top1_total': total_top1_predictions,
            'total_dividendos': round(total_dividendos, 1),
            'top3_accuracy': round(top3_accuracy, 2),
            'top3_correct': top3_correct,
            'top3_total': total_top3_predictions,
            'top4_accuracy': round(top4_accuracy, 2),
            'top4_correct': top4_correct,
            'top4_total': total_top4_predictions,
            'rango_fechas': f"{df['fecha_carrera'].min()} a {df['fecha_carrera'].max()}"
        }
        
    except Exception as e:
        print(f"Error calculando precisión del modelo: {e}")
        import traceback
        traceback.print_exc()
        return {
            'error': str(e),
            'mensaje': 'Error al calcular precisión del modelo'
        }
