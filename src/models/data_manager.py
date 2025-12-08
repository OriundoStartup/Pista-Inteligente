import sqlite3
import pandas as pd
import itertools
import functools

import os
import json
import joblib
import numpy as np

@functools.lru_cache(maxsize=1)
def cargar_datos(nombre_db='hipica_data.db'):
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

def cargar_datos_3nf(nombre_db='hipica_data.db'):
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

def cargar_programa(nombre_db='hipica_data.db'):
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
            # Filtro opcional: Mostrar solo programas futuros o >= hoy? 
            # El usuario dice "fecha futura o fecha que tenga el programa". 
            # Mejor mostrar TODO lo que hay en la tabla programa_carreras, ordenado.
            # df_programa = df_programa[df_programa['fecha_dt'] >= ...] 

            
    if 'numero' in df_programa.columns and not df_programa.empty:
        # Assuming 'nro_carrera' exists or 'carrera' column
        carrera_col = 'nro_carrera' if 'nro_carrera' in df_programa.columns else 'carrera'
        
        grupos = df_programa.groupby(['fecha', 'hipodromo', carrera_col])
        
        for (fecha, hipodromo, nro_carrera), grupo in grupos:
            caballos_df = grupo[['numero', 'nombre', 'jinete', 'stud', 'peso']].copy()
            caballos_df['numero'] = pd.to_numeric(caballos_df['numero'], errors='coerce').fillna(0).astype(int)
            caballos_df = caballos_df.sort_values('numero').reset_index(drop=True)
            
            if ml_available and not df_historial.empty:
                # Usar historial 3NF cargado
                predicciones = analizar_probabilidad_caballos(caballos_df, df_historial)
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

def analizar_probabilidad_caballos(caballos_df, historial_resultados):
    """Analiza probabilidades (fallback) usando datos reales del programa."""
    if historial_resultados.empty or caballos_df.empty:
        return []

    predicciones = []
    
    # Iterar sobre el DataFrame de caballos
    for _, row in caballos_df.iterrows():
        # Clean/Validate values (Robust column names)
        try:
            val_num = row.get('numero') if 'numero' in row else row.get('Nº', 0)
            numero = int(val_num)
        except:
            numero = 0
            
        nombre = row.get('nombre') if 'nombre' in row else row.get('Caballo', f"Caballo {numero}")
        jinete = row.get('jinete') if 'jinete' in row else row.get('Jinete', "Jinete")
        
        # Calcular puntaje basado en historial real
        score = 50.0 # Base
        try:
            # Filtrar historial del caballo
            stats_caballo = historial_resultados[historial_resultados['caballo'] == nombre]
            
            if not stats_caballo.empty:
                # Carreras recientes (últimas 5)
                recientes = stats_caballo.head(5)
                
                # Bonus por victorias
                victorias = len(stats_caballo[stats_caballo['posicion'] == 1])
                score += (victorias * 5.0)
                
                # Bonus por Top 3 reciente
                top3 = len(recientes[recientes['posicion'] <= 3])
                score += (top3 * 3.0)
                
                # Penalización por malos resultados recientes
                malos = len(recientes[recientes['posicion'] > 8])
                score -= (malos * 2.0)
                
                # Factor de velocidad (si existe tiempo)
                # (Simplificado por ahora)
                
                # Cap score 10-99
                score = max(10.0, min(99.0, score))
            else:
                 # Si es debutante o sin data, score conservador
                 score = 45.0
                 
        except Exception as e:
            print(f"Error calculando score para {nombre}: {e}")
            score = 40.0

        predicciones.append({
            'numero': numero,
            'caballo': nombre,
            'jinete': jinete,
            'puntaje_ia': round(score, 1),
            'prob_top3': 0 # Se calculará después o en UI
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
        jinetes_stats['eficiencia'] = (jinetes_stats['ganadas'] / jinetes_stats['carreras']) * 100
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
