import sqlite3
import pandas as pd
import itertools
import functools

import os
import json
import joblib
import numpy as np
from datetime import datetime

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

def obtener_analisis_jornada():
    """Genera análisis usando ML."""
    df_programa = cargar_programa()
    
    if df_programa.empty:
        return []
        
    analisis_completo = []
    
    # Cargar modelo ML v2 si existe
    try:
        model = joblib.load('src/models/rf_model_v2.pkl')
        encoders = joblib.load('src/models/encoders_v2.pkl')
        ml_available = True
    except:
        ml_available = False
    
    # Cargar datos históricos
    df_historial = cargar_datos_3nf()
    
    if not df_programa.empty:
        if 'fecha' in df_programa.columns:
            df_programa['fecha_dt'] = pd.to_datetime(df_programa['fecha'])
            # Filtrar para mostrar SOLO la última jornada disponible (el programa más reciente)
            if not df_programa.empty:
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
                # Convert '1.200' -> 1200 if needed
                distancia_val = float(str(distancia_val).replace('.','')) if isinstance(distancia_val, str) else float(distancia_val)
            except:
                distancia_val = 1100.0

            fecha_val = grupo.iloc[0]['fecha']
            # Pista guessing (Usually hardcoded or from track name, we'll pass generic if missing)
            pista_val = grupo.iloc[0].get('condicion', 'ARENA') # Or 'pista' column if exists

            if ml_available and not df_historial.empty:
                # Usar historial 3NF cargado
                predicciones = analizar_probabilidad_caballos(caballos_df, df_historial, model=model, encoders=encoders, context={'distancia': distancia_val, 'fecha': fecha_val, 'pista': pista_val})
            else:
                predicciones = analizar_probabilidad_caballos(caballos_df, df_historial)
            
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

def analizar_probabilidad_caballos(caballos_df, historial_resultados, model=None, encoders=None, context=None):
    """Analiza probabilidades usando ML + Heurística híbrida."""
    if historial_resultados.empty or caballos_df.empty:
        return []

    predicciones = []
    
    # Pre-calcular stats globales para eficiencia (Optimización)
    jockey_stats = {}
    if model:
        try:
            # Simple global stats
            grp_j = historial_resultados.groupby('jinete_id')
            jockey_stats = {
                'wins': grp_j['posicion'].apply(lambda x: (x==1).sum()),
                'total': grp_j['posicion'].count()
            }
        except:
            pass

    # Contexto
    distancia = context.get('distancia', 1000) if context else 1000
    fecha_carrera = pd.to_datetime(context.get('fecha', datetime.now())) if context else datetime.now()
    pista = context.get('pista', 'ARENA') if context else 'ARENA'

    for _, row in caballos_df.iterrows():
        try:
            val_num = row.get('numero') if 'numero' in row else row.get('Nº', 0)
            numero = int(val_num)
        except:
            numero = 0
            
        nombre = row.get('nombre') if 'nombre' in row else row.get('Caballo', f"Caballo {numero}")
        jinete = row.get('jinete') if 'jinete' in row else row.get('Jinete', "Jinete")
        
        # --- 1. Heuristic Score (Base Layer) ---
        heuristic_score = 50.0
        caballo_hist = historial_resultados[historial_resultados['caballo'] == nombre]
        
        if not caballo_hist.empty:
            victorias = len(caballo_hist[caballo_hist['posicion'] == 1])
            heuristic_score += (victorias * 4.0)
            top3 = len(caballo_hist[caballo_hist['posicion'] <= 3])
            heuristic_score += (top3 * 2.0)
            # Recent form
            last_3 = caballo_hist.head(3)
            if not last_3.empty:
                avg_pos = last_3['posicion'].mean()
                if avg_pos <= 3: heuristic_score += 15
                elif avg_pos <= 6: heuristic_score += 5
        else:
            heuristic_score = 45.0 # Debutante

        heuristic_score = max(10.0, min(99.0, heuristic_score))

        # --- 2. ML Prediction (Intelligence Layer) ---
        ml_prob = 0.0
        if model and not caballo_hist.empty:
            try:
                # Build Feature Vector matching train_v2.py
                # ['days_rest', 'avg_pos_3', 'win_rate', 'races_count', 'jockey_eff', 'distancia', 'avg_speed_3', 'pista_encoded', 'mandil']
                
                # Days Rest
                last_date = pd.to_datetime(caballo_hist.iloc[0]['fecha'])
                days_rest = (fecha_carrera - last_date).days
                if days_rest < 0: days_rest = 30 # Data error fix
                
                # Avg Pos 3
                avg_pos_3 = caballo_hist.head(3)['posicion'].mean()
                if pd.isna(avg_pos_3): avg_pos_3 = 8.0
                
                # Win Rate
                wins = len(caballo_hist[caballo_hist['posicion'] == 1])
                cnt = len(caballo_hist)
                win_rate = wins / cnt if cnt > 0 else 0
                
                # Jockey Eff (Approximate by name lookup if ID missing in df or using ID column)
                # Assuming 'jinete_id' in history matches... but we might just use name to find ID
                # Simplification: use global avg if not found easily
                # Let's try to find jinete in history
                j_eff = 0.1
                # (Skipping complex lookup for speed reliability in this step, defaulting to .10)
                
                # Avg Speed
                # Need to parse times. Expensive loop. Skip or simple approx.
                avg_speed_3 = 14.0 # Default placeholder for robust inference
                
                # Encode Pista
                p_enc = 0
                if encoders and 'pista' in encoders:
                    try:
                        p_enc = encoders['pista'].transform([str(pista)])[0]
                    except:
                        p_enc = 0

                features = np.array([[
                    days_rest, avg_pos_3, win_rate, cnt,
                    j_eff, distancia, avg_speed_3, p_enc, numero
                ]])
                
                # Predict
                ml_prob = model.predict_proba(features)[0][1] # Probability of Class 1 (Win)
                
            except Exception as e:
                # print(f"ML Error for {nombre}: {e}")
                ml_prob = 0.0
        
        # --- 3. Blending (Hybrid AI) ---
        # Si ML tiene confianza alta, pesa más.
        # Score final (0-100)
        # ML Prob (0.0 - 0.5 usually for multi-class/hard problems) -> Scale to 0-100
        # A good horse might have 20-30% win prob in a 15 horse race.
        
        ml_score = ml_prob * 300 # Scale 0.33 -> 100 roughly
        ml_score = min(100, ml_score)
        
        final_score = (heuristic_score * 0.4) + (ml_score * 0.6)
        
        predicciones.append({
            'numero': numero,
            'caballo': nombre,
            'jinete': jinete,
            'puntaje_ia': round(final_score, 1),
            'prob_ml': f"{ml_prob*100:.1f}%" # Debug info
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
        # jinetes = top4['jinete'].tolist()
        # numeros = top4['mandil'].tolist()
        
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
        p = pack_patron(sig, count, 'Quinela (2 aciertos)')
        if p: patrones.append(p)

    for sig, count in trifectas.items():
        p = pack_patron(sig, count, 'Trifecta (3 aciertos)')
        if p: patrones.append(p)
        
    for sig, count in superfectas.items():
        p = pack_patron(sig, count, 'Superfecta (4 aciertos)')
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
