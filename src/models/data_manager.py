import sqlite3
import pandas as pd
import itertools
import functools

import os
import json
import joblib
import numpy as np
from datetime import datetime
from .features import FeatureEngineering

@functools.lru_cache(maxsize=1)
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

@functools.lru_cache(maxsize=4)
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

def cargar_programa(nombre_db='data/db/hipica_data.db'):
    """Carga el programa de carreras desde la base de datos."""
    if not os.path.exists(nombre_db) and os.path.exists(f'data/db/{nombre_db}'):
        nombre_db = f'data/db/{nombre_db}'
        
    try:
        conn = sqlite3.connect(nombre_db)
        # Try to join with normalized tables if they exist, otherwise raw
        try:
             # Normalized programmatic join
             query = """
                SELECT 
                    pc.fecha, h.nombre as hipodromo, pc.nro_carrera, pc.hora, pc.distancia, pc.condicion,
                    pc.numero, c.nombre, j.nombre as jinete, s.nombre as stud, pc.peso
                FROM programa_carreras pc
                LEFT JOIN hipodromos h ON pc.hipodromo = h.nombre OR h.codigo = pc.hipodromo
                LEFT JOIN caballos c ON pc.caballo_id = c.id
                LEFT JOIN jinetes j ON pc.jinete_id = j.id
                LEFT JOIN studs s ON pc.stud_id = s.id
             """
             df = pd.read_sql(query, conn)
        except:
             # Fallback to simple select if flat table
             df = pd.read_sql("SELECT * FROM programa_carreras", conn)
             
        conn.close()
        return df
    except:
        return pd.DataFrame()

@functools.lru_cache(maxsize=1)
def obtener_analisis_jornada():
    """Genera análisis usando ML."""
    df_programa = cargar_programa()
    
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
                today = datetime.now().strftime('%Y-%m-%d')
                future_programs = df_programa[df_programa['fecha'] >= today]
                
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
            caballos_df = grupo[['numero', 'nombre', 'jinete', 'stud', 'peso']].copy()
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
    
    # 1. Prepare Input for FeatureEngineering
    # We need to construct a DF that looks like 'get_raw_data' result but for the current race candidates.
    # We essentially need to find their history to calc lag features.
    
    # Optimization: Filter history to only relevant horses/jockeys to speed up lookups
    # But for now, we pass full history to 'fe' or let 'fe' handle it? 
    # Current 'fe.transform' expects a DF with history COLUMNS pre-calculated if logic is complex
    # OR it calculates them from the rows provided. 
    
    # Problem: 'fe.transform' calculates rolling stats on the PROVIDED df.
    # If we provide a DF with just 1 row per horse (current race), rolling stats will be NaN or 0.
    # WE NEED TO APPEND CURRENT RACE TO HISTORY TO CALC ROLLING, THEN PREDICT ON LAST ROW.
    
    # Strategy:
    # For each horse in current race:
    # 1. Get its history from historial_resultados
    # 2. Append a "current" row with race context (dist, pista, etc)
    # 3. Call fe.transform on this combined small DF
    # 4. Extract the last row (the current prediction input)
    
    # Context
    distancia = context.get('distancia', 1000) if context else 1000
    fecha_carrera = pd.to_datetime(context.get('fecha', datetime.now())) if context else datetime.now()
    pista = context.get('pista', 'ARENA') if context else 'ARENA'
    
    # Pre-filter history
    relevant_horses = set(caballos_df['nombre'].values)
    # We match by Name because ID might be missing in program or distinct.
    # Ideally should use ID. Assuming 'nombre' is key.
    
    # Create rows for batch prediction
    batch_rows = []
    horse_indices = []

    for idx, row in caballos_df.iterrows():
        nombre = row.get('nombre')
        val_num = row.get('numero', 0)
        jinete_nombre = row.get('jinete', 'Jinete')
        peso_val = row.get('peso', 470)
        
        # Heuristic Score (legacy fallback/hybrid factor)
        heuristic_score = 50.0
        # Find horse checks
        caballo_hist = historial_resultados[historial_resultados['caballo'] == nombre].sort_values('fecha')
        
        if not caballo_hist.empty:
            # Simple stats for legacy score
            wins = len(caballo_hist[caballo_hist['posicion'] == 1])
            heuristic_score += (wins * 2.0)
        else:
            heuristic_score = 45.0 # Debutante

        # ML Prep
        if model and fe:
            # Construct a row representing this race attempt
            # We need to map columns expected by 'fe.transform' logic IF it runs full calculation
            # But 'fe.transform' expects raw SQL columns: 
            # [posicion, mandil, tiempo, peso_fs, dividendo, caballo_id, jinete_id, fecha, hipodromo_id, distancia, pista, condicion]
            
            # We fake dummy IDs if needed or use name-based lookups if we refactored FE to use names?
            # FE uses 'caballo_id', 'jinete_id'.
            # We must map names to IDs from history.
            
            c_id = 0
            j_id = 0
            if not caballo_hist.empty:
                c_id = caballo_hist.iloc[0]['caballo_id']
                
            # Find Jinete ID
            j_hist = historial_resultados[historial_resultados['jinete'] == jinete_nombre]
            if not j_hist.empty:
                j_id = j_hist.iloc[0]['jinete_id']

            # Create the "Current" row
            # Note: 'posicion', 'tiempo', 'dividendo' are unknown (Target), set to NaN or 0
            current_row = {
                'fecha': fecha_carrera,
                'caballo_id': c_id,
                'jinete_id': j_id,
                'distancia': distancia,
                'pista': pista,
                'peso_fs': peso_val,
                'mandil': val_num,
                'tiempo': 0, # Unknown
                'posicion': 0, # Unknown
                'is_win': 0 # Unknown
            }
            
            # Combine history + current
            # We need strictly the columns that 'fe' uses for grouping
            cols_needed = ['fecha', 'caballo_id', 'jinete_id', 'distancia', 'pista', 'peso_fs', 'mandil', 'tiempo', 'posicion']
            
            # Reduce history to needed cols
            h_subset = caballo_hist[cols_needed].copy()
            # Append current
            h_subset = pd.concat([h_subset, pd.DataFrame([current_row])], ignore_index=True)
            
            # Run FE
            # Note: calculating for just one horse is fast enough
            try:
                # Transform constructs features including rolling windows
                # The last row is our target
                feats = fe.transform(h_subset, is_training=False)
                last_feat = feats.iloc[-1:].copy()
                
                # Predict
                prob = model.predict_proba(last_feat)[0][1]
                ml_score = prob * 100 * 2.5 # Scale roughly
                ml_score = min(99, ml_score)
                
            except Exception as e:
                # print(f"ML Error for {nombre}: {e}")
                ml_score = 50.0 # Neural fallback
        else:
             ml_score = 50.0

        # Hybrid
        final_score = (heuristic_score * 0.3) + (ml_score * 0.7)
        
        predicciones.append({
            'numero': int(val_num),
            'caballo': nombre,
            'jinete': jinete_nombre,
            'puntaje_ia': round(final_score, 1),
            'prob_ml': f"{ml_score:.1f}"
        })
        
    predicciones.sort(key=lambda x: x['puntaje_ia'], reverse=True)
    return predicciones[:4]

def obtener_lista_hipodromos():
    """Obtiene la lista única de hipódromos."""
    try:
        df = cargar_datos_3nf()
        if not df.empty:
            return sorted(df['hipodromo'].unique().tolist())
        df = cargar_datos()
        if not df.empty and 'hipodromo' in df.columns:
             return sorted(df['hipodromo'].unique().tolist())
        return []
    except:
        return []

def obtener_patrones_la_tercera(hipodromo_filtro=None):
    """Busca patrones de resultados repetidos (Quinela, Trifecta, Superfecta)."""
    df = cargar_datos_3nf()
    if df.empty: return []

    if hipodromo_filtro and hipodromo_filtro != 'Todos':
        df = df[df['hipodromo'] == hipodromo_filtro]

    # Agrupar por carrera
    carreras_groups = df.groupby(['hipodromo', 'fecha', 'nro_carrera'])
    
    # Contadores
    quinelas = {}
    trifectas = {}
    superfectas = {}
    
    # Detalles para reconstruir vista
    # Key: Signature -> Sample List of details
    details_map = {} 

    for (hip, fecha, nro), grupo in carreras_groups:
        # Ordenar por llegada
        llegada = grupo.sort_values('posicion')
        top4 = llegada.head(4)
        
        if len(top4) < 2: continue
        
        # Extract data
        caballos = top4['caballo'].tolist()
        
        # Quinela (Top 2 - Any Order for Box, but let's check Exacta for now or sorted tuple)
        # User said "Quinela", usually 1-2 any order.
        sig_quinela = tuple(sorted(caballos[:2])) 
        if len(sig_quinela) == 2:
            quinelas[sig_quinela] = quinelas.get(sig_quinela, 0) + 1
            if sig_quinela not in details_map:
                details_map[sig_quinela] = top4.iloc[:2].to_dict('records')

        # Trifecta (Top 3 - Exact Order usually)
        if len(top4) >= 3:
            sig_trifecta = tuple(caballos[:3])
            trifectas[sig_trifecta] = trifectas.get(sig_trifecta, 0) + 1
            if sig_trifecta not in details_map:
                details_map[sig_trifecta] = top4.iloc[:3].to_dict('records')

        # Superfecta (Top 4 - Exact Order)
        if len(top4) >= 4:
            sig_superfecta = tuple(caballos[:4])
            superfectas[sig_superfecta] = superfectas.get(sig_superfecta, 0) + 1
            if sig_superfecta not in details_map:
                details_map[sig_superfecta] = top4.iloc[:4].to_dict('records')

    patrones = []

    # Filtrar >= 2
    def pack_patron(signature, count, tipo):
        if count >= 2:
            items = []
            raw_items = details_map.get(signature, [])
            for r in raw_items:
                items.append({
                    'puesto': int(r['posicion']) if pd.notna(r['posicion']) else 0,
                    'numero': int(r['mandil']) if pd.notna(r['mandil']) else 0,
                    'caballo': r['caballo'],
                    'jinete': r['jinete']
                })
            return {'tipo': tipo, 'veces': count, 'detalle': items}
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

def obtener_estadisticas_generales():
    """Calcula estadísticas generales de rendimiento."""
    df = cargar_datos_3nf()
    if df.empty:
        return {'jinetes': [], 'caballos': [], 'pistas': [], 'total_carreras': 0}

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
        
        return {
            'jinetes': top_jinetes,
            'caballos': top_caballos,
            'pistas': track_stats,
            'total_carreras': len(df)
        }
        
    except Exception as e:
        print(f"Error calculando estadisticas: {e}")
        return {'jinetes': [], 'caballos': [], 'pistas': [], 'total_carreras': 0}

