# -*- coding: utf-8 -*-
"""
Modelo de Machine Learning para predecir llegadas ganadoras en carreras hípicas.
Usa Random Forest para analizar patrones históricos y generar predicciones.
"""

import sys
import io
import pandas as pd
import numpy as np
import sqlite3
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import joblib
import os
from datetime import datetime

# Configurar encoding UTF-8 para Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

class PredictorHipico:
    """Predictor de llegadas usando Machine Learning."""
    
    def __init__(self, db_path='hipica_data.db'):
        self.db_path = db_path
        self.modelo_primero = None
        self.modelo_segundo = None
        self.modelo_tercero = None
        self.le_hipodromo = LabelEncoder()
        
    def cargar_datos_historicos(self):
        """Carga datos históricos desde la base de datos."""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql("SELECT * FROM resultados ORDER BY fecha DESC LIMIT 500", conn)
        conn.close()
        return df
    
    def preparar_features(self, df):
        """Prepara features para el modelo de ML."""
        # Codificar hipódromo
        df['hipodromo_encoded'] = self.le_hipodromo.fit_transform(df['hipodromo'])
        
        # Extraer características de fecha
        df['fecha'] = pd.to_datetime(df['fecha'])
        df['dia_semana'] = df['fecha'].dt.dayofweek
        df['mes'] = df['fecha'].dt.month
        
        # Features: hipódromo, número de carrera, día de semana, mes
        X = df[['hipodromo_encoded', 'nro_carrera', 'dia_semana', 'mes']]
        
        # Targets: primero, segundo, tercero
        y_primero = df['primero']
        y_segundo = df['segundo']
        y_tercero = df['tercero']
        
        return X, y_primero, y_segundo, y_tercero
    
    def entrenar_modelo(self):
        """Entrena los modelos de predicción."""
        print("🤖 Entrenando modelo de Machine Learning...")
        
        df = self.cargar_datos_historicos()
        
        if df.empty or len(df) < 50:
            print("⚠️ No hay suficientes datos para entrenar el modelo.")
            return False
        
        # Limpiar datos: eliminar filas con valores NaN
        df = df.dropna(subset=['primero', 'segundo', 'tercero', 'hipodromo', 'nro_carrera'])
        
        if len(df) < 50:
            print("⚠️ No hay suficientes datos válidos después de limpiar.")
            return False
        
        X, y_primero, y_segundo, y_tercero = self.preparar_features(df)
        
        # Entrenar modelo para primer lugar
        self.modelo_primero = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.modelo_primero.fit(X, y_primero)
        
        # Entrenar modelo para segundo lugar
        self.modelo_segundo = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.modelo_segundo.fit(X, y_segundo)
        
        # Entrenar modelo para tercer lugar
        self.modelo_tercero = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.modelo_tercero.fit(X, y_tercero)
        
        # Guardar modelos
        joblib.dump(self.modelo_primero, 'modelo_primero.pkl')
        joblib.dump(self.modelo_segundo, 'modelo_segundo.pkl')
        joblib.dump(self.modelo_tercero, 'modelo_tercero.pkl')
        joblib.dump(self.le_hipodromo, 'label_encoder.pkl')
        
        print("[OK] Modelos entrenados y guardados exitosamente.")
        return True
    
    def cargar_modelos(self):
        """Carga modelos previamente entrenados."""
        try:
            self.modelo_primero = joblib.load('modelo_primero.pkl')
            self.modelo_segundo = joblib.load('modelo_segundo.pkl')
            self.modelo_tercero = joblib.load('modelo_tercero.pkl')
            self.le_hipodromo = joblib.load('label_encoder.pkl')
            return True
        except:
            return False
    
    def predecir_carrera(self, hipodromo, nro_carrera, caballos_participantes):
        """
        Predice las llegadas para una carrera específica.
        
        Args:
            hipodromo: Nombre del hipódromo
            nro_carrera: Número de carrera
            caballos_participantes: Lista de números de caballos
            
        Returns:
            DataFrame con predicciones y probabilidades
        """
        # Cargar modelos si no están cargados
        if self.modelo_primero is None:
            if not self.cargar_modelos():
                if not self.entrenar_modelo():
                    return pd.DataFrame()
        
        # Preparar features para predicción
        fecha_actual = datetime.now()
        
        try:
            hipodromo_encoded = self.le_hipodromo.transform([hipodromo])[0]
        except:
            # Si el hipódromo no está en el encoder, usar el primero
            hipodromo_encoded = 0
        
        X_pred = pd.DataFrame({
            'hipodromo_encoded': [hipodromo_encoded],
            'nro_carrera': [nro_carrera],
            'dia_semana': [fecha_actual.weekday()],
            'mes': [fecha_actual.month]
        })
        
        # Obtener probabilidades para cada posición
        prob_primero = self.modelo_primero.predict_proba(X_pred)[0]
        prob_segundo = self.modelo_segundo.predict_proba(X_pred)[0]
        prob_tercero = self.modelo_tercero.predict_proba(X_pred)[0]
        
        # Crear diccionario de probabilidades por caballo
        clases_primero = self.modelo_primero.classes_
        clases_segundo = self.modelo_segundo.classes_
        clases_tercero = self.modelo_tercero.classes_
        
        predicciones = []
        
        for caballo in caballos_participantes:
            # Buscar probabilidad para este caballo
            prob_1 = prob_primero[np.where(clases_primero == caballo)[0][0]] if caballo in clases_primero else 0
            prob_2 = prob_segundo[np.where(clases_segundo == caballo)[0][0]] if caballo in clases_segundo else 0
            prob_3 = prob_tercero[np.where(clases_tercero == caballo)[0][0]] if caballo in clases_tercero else 0
            
            # Calcular probabilidad combinada de figuración (top 3)
            prob_figuracion = prob_1 + prob_2 + prob_3
            
            predicciones.append({
                'Caballo': f"Nº {caballo}",
                'Prob_1ro': round(prob_1 * 100, 1),
                'Prob_2do': round(prob_2 * 100, 1),
                'Prob_3ro': round(prob_3 * 100, 1),
                'Prob_Figuracion': round(prob_figuracion * 100, 1)
            })
        
        df_pred = pd.DataFrame(predicciones)
        df_pred = df_pred.sort_values('Prob_1ro', ascending=False)
        
        return df_pred
    
    def generar_predicciones_jornada(self):
        """Genera predicciones para todas las carreras del programa."""
        conn = sqlite3.connect(self.db_path)
        
        try:
            df_programa = pd.read_sql("SELECT * FROM programa_carreras", conn)
        except:
            print("⚠️ No hay programa de carreras disponible.")
            conn.close()
            return pd.DataFrame()
        
        conn.close()
        
        if df_programa.empty:
            print("⚠️ El programa de carreras está vacío.")
            return pd.DataFrame()
        
        print(f"\n🔮 Generando predicciones para {len(df_programa['nro_carrera'].unique())} carreras...")
        
        predicciones_totales = []
        
        # Agrupar por carrera
        grupos = df_programa.groupby(['fecha', 'hipodromo', 'nro_carrera'])
        
        for (fecha, hipodromo, nro_carrera), grupo in grupos:
            # Obtener lista de números de caballos
            try:
                caballos = pd.to_numeric(grupo['numero'], errors='coerce').dropna().astype(int).tolist()
            except:
                continue
            
            if not caballos:
                continue
            
            # Generar predicción
            df_pred = self.predecir_carrera(hipodromo, nro_carrera, caballos)
            
            if not df_pred.empty:
                # Agregar info de la carrera
                df_pred['Hipodromo'] = hipodromo
                df_pred['Carrera'] = nro_carrera
                df_pred['Fecha'] = fecha
                
                predicciones_totales.append(df_pred)
                
                print(f"  [OK] {hipodromo} - Carrera {nro_carrera}: Top 3 predicho")
        
        if predicciones_totales:
            df_final = pd.concat(predicciones_totales, ignore_index=True)
            
            # Guardar en base de datos
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Crear tabla de predicciones
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS predicciones (
                    fecha TEXT,
                    hipodromo TEXT,
                    nro_carrera INTEGER,
                    caballo TEXT,
                    prob_1ro REAL,
                    prob_2do REAL,
                    prob_3ro REAL,
                    prob_figuracion REAL
                )
            ''')
            
            # Limpiar predicciones antiguas
            cursor.execute('DELETE FROM predicciones')
            
            # Insertar nuevas predicciones
            for idx, row in df_final.iterrows():
                cursor.execute('''
                    INSERT INTO predicciones VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    row['Fecha'],
                    row['Hipodromo'],
                    row['Carrera'],
                    row['Caballo'],
                    row['Prob_1ro'],
                    row['Prob_2do'],
                    row['Prob_3ro'],
                    row['Prob_Figuracion']
                ))
            
            conn.commit()
            conn.close()
            
            print(f"\n[OK] Predicciones guardadas en la base de datos.")
            return df_final
        
        return pd.DataFrame()


if __name__ == "__main__":
    predictor = PredictorHipico()
    
    # Entrenar modelo
    predictor.entrenar_modelo()
    
    # Generar predicciones para la jornada
    df_predicciones = predictor.generar_predicciones_jornada()
    
    if not df_predicciones.empty:
        print("\n" + "="*60)
        print("RESUMEN DE PREDICCIONES")
        print("="*60)
        
        for hipodromo in df_predicciones['Hipodromo'].unique():
            print(f"\n{hipodromo}:")
            df_hip = df_predicciones[df_predicciones['Hipodromo'] == hipodromo]
            
            for carrera in df_hip['Carrera'].unique():
                df_car = df_hip[df_hip['Carrera'] == carrera].head(3)
                print(f"\n  Carrera {carrera} - Top 3 Predicho:")
                for idx, row in df_car.iterrows():
                    print(f"    {row['Caballo']}: {row['Prob_1ro']}% (1º), {row['Prob_Figuracion']}% (Fig.)")
