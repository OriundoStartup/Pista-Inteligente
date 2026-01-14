import sqlite3
import pandas as pd
import os
import json
import joblib
import numpy as np
from datetime import datetime, timedelta


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

# [CLEANUP] Legacy in-memory cache and local inference logic removed.
# Now using Supabase for cloud data.


# --- SUPABASE INTEGRATION ---
def _init_supabase():
    """Initialize Supabase client."""
    try:
        from supabase import create_client
        from dotenv import load_dotenv
        load_dotenv()
        
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('SUPABASE_KEY')
        
        if not url or not key:
            print("⚠️ SUPABASE_URL o SUPABASE_KEY no configurados en .env")
            return None
            
        return create_client(url, key)
    except Exception as e:
        print(f"⚠️ Supabase Init Warning: {e}")
        return None

def obtener_predicciones_supabase(fecha_min_str):
    """Obtiene predicciones futuras desde Supabase."""
    supabase = _init_supabase()
    if not supabase:
        return []
    
    try:
        # Query predicciones table
        response = supabase.table('predicciones')\
            .select('*, carreras(nro_carrera, hora, distancia, jornadas(fecha, hipodromos(nombre)))')\
            .gte('created_at', fecha_min_str)\
            .order('rank_predicho', desc=False)\
            .execute()
        
        return response.data if response.data else []
    except Exception as e:
        print(f"⚠️ Error Supabase Read: {e}")
        return []

def obtener_analisis_jornada(use_firestore=False):
    """
    Genera análisis usando Supabase (Full Cloud).
    Parámetro use_firestore se mantiene por compatibilidad pero se ignora.
    """
    chile_time = datetime.utcnow() - timedelta(hours=3)
    today_str = chile_time.strftime('%Y-%m-%d')

    try:
        supabase_data = obtener_predicciones_supabase(today_str)
    except Exception as e:
        print(f"❌ Error Critical Supabase: {e}")
        return []

    if not supabase_data:
        return []

    # Group predictions by race
    races_dict = {}
    
    for pred in supabase_data:
        carrera_data = pred.get('carreras', {}) or {}
        jornada_data = carrera_data.get('jornadas', {}) or {}
        hipodromo_data = jornada_data.get('hipodromos', {}) or {}
        
        race_key = pred.get('carrera_id', 'unknown')
        
        if race_key not in races_dict:
            races_dict[race_key] = {
                'hipodromo': hipodromo_data.get('nombre', 'Unknown'),
                'carrera': carrera_data.get('nro_carrera', 0),
                'fecha': jornada_data.get('fecha', today_str),
                'hora': carrera_data.get('hora', '00:00'),
                'distancia': carrera_data.get('distancia', 0),
                'predicciones': []
            }
        
        races_dict[race_key]['predicciones'].append({
            'numero': pred.get('numero_caballo', 0),
            'caballo': pred.get('caballo', 'N/A'),
            'jinete': pred.get('jinete', 'N/A'),
            'puntaje_ia': round((pred.get('probabilidad', 0) or 0) * 100, 1),
            'prob_ml': f"{(pred.get('probabilidad', 0) or 0) * 100:.1f}"
        })

    analisis_completo = list(races_dict.values())
    
    # Sort predictions within each race and limit to Top 4
    for race in analisis_completo:
        race['predicciones'].sort(key=lambda x: x['puntaje_ia'], reverse=True)
        race['predicciones'] = race['predicciones'][:4]
    
    # Sort races by date, hipodromo, number
    analisis_completo.sort(key=lambda x: (x['fecha'], x['hipodromo'], x['carrera']))
    return analisis_completo

def obtener_lista_hipodromos():
    """Obtiene la lista única de hipódromos."""
    return ['Club Hípico de Santiago', 'Hipódromo Chile', 'Valparaíso Sporting']
        

             


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
            # Fix: Firestore version returns 'predicciones', not 'caballos'.
            # 'predicciones' contains enriched horse data.
            caballos_carrera = carrera.get('caballos', [])
            if not caballos_carrera and 'predicciones' in carrera:
                 caballos_carrera = carrera['predicciones']
            
            # Normalize names
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
        SELECT DISTINCT
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
