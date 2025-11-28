import sqlite3
import pandas as pd
import itertools
import streamlit as st
import os

@st.cache_data(ttl=86400)
def cargar_datos(nombre_db='hipica_data.db'):
    """Carga los datos desde la base de datos SQLite."""
    if not os.path.exists(nombre_db):
        return pd.DataFrame()
        
    try:
        conn = sqlite3.connect(nombre_db)
        df = pd.read_sql("SELECT * FROM resultados", conn)
        conn.close()
        return df
    except Exception as e:
        return pd.DataFrame()

def cargar_programa(nombre_db='hipica_data.db'):
    """Carga el programa de carreras desde la base de datos."""
    try:
        conn = sqlite3.connect(nombre_db)
        df = pd.read_sql("SELECT * FROM programa_carreras", conn)
        conn.close()
        return df
    except:
        return pd.DataFrame()

import json

def procesar_caballos_programa(caballos_str):
    """Parsea la columna de caballos que puede venir como JSON o texto simple."""
    try:
        # Intentar parsear como JSON
        datos = json.loads(caballos_str)
        if isinstance(datos, list):
            # Formato: [{"numero": 1, "nombre": "Caballo"}, ...]
            return [d['nombre'] for d in datos], [int(d['numero']) for d in datos]
    except:
        pass
        
    try:
        # Intentar formato simple CSV: "1, 2, 3" o nombres
        partes = caballos_str.split(',')
        nombres = []
        numeros = []
        for p in partes:
            p = p.strip()
            if p.isdigit():
                numeros.append(int(p))
                nombres.append(f"#{p}")
            else:
                nombres.append(p)
                # Intentar extraer número si viene como "1. Nombre"
                import re
                match = re.match(r"(\d+)\.", p)
                if match:
                    numeros.append(int(match.group(1)))
                else:
                    numeros.append(0) # Sin número identificado
        return nombres, numeros
    except:
        return [], []

def obtener_analisis_jornada():
    """
    Carga el programa y genera un análisis completo para cada carrera.
    Retorna una lista de diccionarios con la info de la carrera y sus predicciones.
    """
    df_programa = cargar_programa()
    df_historial = cargar_datos()
    
    if df_programa.empty:
        return []
        
    analisis_completo = []
    
    # Agrupar por hipódromo y ordenar
    df_programa = df_programa.sort_values(['hipodromo', 'nro_carrera'])
    
    for _, row in df_programa.iterrows():
        nombres_caballos, numeros_caballos = procesar_caballos_programa(row['caballos'])
        
        # Si tenemos nombres reales, intentamos buscar por nombre en el historial (más preciso)
        # Si no, usamos los números (como fallback, aunque menos preciso si cambian los caballos)
        
        # Para este ejemplo, usaremos la lógica de números que ya tenías, 
        # pero idealmente deberíamos normalizar nombres.
        
        # Calcular predicciones
        predicciones = analizar_probabilidad_caballos(numeros_caballos, df_historial)
        
        analisis_completo.append({
            'hipodromo': row['hipodromo'],
            'carrera': row['nro_carrera'],
            'fecha': row['fecha'],
            'caballos': list(zip(numeros_caballos, nombres_caballos)),
            'predicciones': predicciones
        })
        
    return analisis_completo

def analizar_probabilidad_caballos(caballos_jornada, historial_resultados):
    """
    Analiza probabilidades para los caballos de la jornada.
    Retorna un DataFrame con el Top 5 de combinaciones probables.
    """
    if historial_resultados.empty or not caballos_jornada:
        return pd.DataFrame()

    stats_caballos = {}
    
    # Calcular estadísticas para cada caballo participante
    for caballo in caballos_jornada:
        # Frecuencia en cada posición
        freq_1 = len(historial_resultados[historial_resultados['primero'] == caballo])
        freq_2 = len(historial_resultados[historial_resultados['segundo'] == caballo])
        freq_3 = len(historial_resultados[historial_resultados['tercero'] == caballo])
        
        total_top3 = freq_1 + freq_2 + freq_3
        
        stats_caballos[caballo] = {
            '1ro': freq_1,
            '2do': freq_2,
            '3ro': freq_3,
            'top3': total_top3
        }
        
    # Generar combinaciones (Trifectas)
    combinaciones = []
    
    caballos_con_historial = [c for c in caballos_jornada if stats_caballos[c]['top3'] > 0]
    candidatos = caballos_con_historial if len(caballos_con_historial) >= 3 else caballos_jornada
    
    if len(candidatos) < 3:
        return pd.DataFrame()

    candidatos.sort(key=lambda x: stats_caballos[x]['top3'], reverse=True)
    candidatos_top = candidatos[:8]

    for p in itertools.permutations(candidatos_top, 3):
        c1, c2, c3 = p
        score = (stats_caballos[c1]['1ro'] * 5 + stats_caballos[c1]['top3']) + \
                (stats_caballos[c2]['2do'] * 3 + stats_caballos[c2]['top3']) + \
                (stats_caballos[c3]['3ro'] * 1 + stats_caballos[c3]['top3'])
                
        combinaciones.append({
            'Combinación': f"{c1}-{c2}-{c3}",
            'Score': score,
            '1º Lugar': c1,
            '2º Lugar': c2,
            '3º Lugar': c3
        })
    
    if not combinaciones:
        return pd.DataFrame()
        
    df_comb = pd.DataFrame(combinaciones)
    df_comb = df_comb.sort_values('Score', ascending=False).head(5)
    
    return df_comb[['Combinación', '1º Lugar', '2º Lugar', '3º Lugar']]

def obtener_patrones_la_tercera():
    """
    Busca patrones que se han repetido exactamente 2 veces.
    Retorna una lista de diccionarios con el detalle.
    """
    df = cargar_datos()
    if df.empty:
        return []
        
    # Contar repeticiones
    conteo = df['llegada_str'].value_counts()
    
    # Filtrar los que tienen exactamente 2 repeticiones
    patrones_dos = conteo[conteo == 2].index.tolist()
    
    resultados = []
    for patron in patrones_dos:
        # Obtener las carreras donde ocurrió
        carreras = df[df['llegada_str'] == patron].sort_values('fecha', ascending=False)
        
        # Calcular una "Probabilidad de Tendencia" simple
        # Si la última vez fue reciente, la probabilidad es mayor
        ultima_fecha = pd.to_datetime(carreras.iloc[0]['fecha'])
        dias_desde_ultimo = (pd.Timestamp.now() - ultima_fecha).days
        
        # Heurística simple: Menos días = Mayor "calor" del patrón
        score = max(10, 100 - dias_desde_ultimo)
        probabilidad = min(95, score)
        
        resultados.append({
            'patron': patron,
            'probabilidad': probabilidad,
            'ultima_fecha': carreras.iloc[0]['fecha'],
            'hipodromo': carreras.iloc[0]['hipodromo'],
            'historial': carreras[['fecha', 'hipodromo', 'nro_carrera']].to_dict('records')
        })
    
    # Ordenar por probabilidad (más recientes primero)
    resultados.sort(key=lambda x: x['probabilidad'], reverse=True)
    return resultados

def obtener_estadisticas_generales():
    """Calcula estadísticas generales de números ganadores."""
    df = cargar_datos()
    if df.empty:
        return {}, pd.DataFrame()
        
    stats = {
        'total_carreras': len(df),
        'hipodromos': df['hipodromo'].nunique(),
        'dias_registrados': df['fecha'].nunique()
    }
    
    # Frecuencia de ganadores (1er lugar)
    top_ganadores = df['primero'].value_counts().reset_index()
    top_ganadores.columns = ['Numero', 'Victorias']
    
    # Frecuencia de 2dos lugares
    top_segundos = df['segundo'].value_counts().reset_index()
    top_segundos.columns = ['Numero', 'Segundos']
    
    # Frecuencia de 3ros lugares
    top_terceros = df['tercero'].value_counts().reset_index()
    top_terceros.columns = ['Numero', 'Terceros']
    
    # Merge para tabla completa
    df_stats = top_ganadores.merge(top_segundos, on='Numero', how='outer').merge(top_terceros, on='Numero', how='outer').fillna(0)
    df_stats['Total Podios'] = df_stats['Victorias'] + df_stats['Segundos'] + df_stats['Terceros']
    df_stats = df_stats.sort_values('Total Podios', ascending=False)
    
    return stats, df_stats

def obtener_top_quinelas():
    """Devuelve las parejas (1ro y 2do) más frecuentes independientemente del orden."""
    df = cargar_datos()
    if df.empty:
        return pd.DataFrame()
        
    quinelas = []
    for _, row in df.iterrows():
        if row['primero'] and row['segundo']:
            # Ordenar par para que 1-2 sea igual a 2-1 (Quinela)
            par = sorted([str(row['primero']), str(row['segundo'])])
            quinelas.append(f"{par[0]} - {par[1]}")
            
    return pd.Series(quinelas).value_counts().head(10).reset_index(name='Frecuencia').rename(columns={'index': 'Quinela'})
