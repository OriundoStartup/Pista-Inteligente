import sqlite3
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os

class HipicaLearner:
    def __init__(self, db_path='hipica_data.db'):
        self.db_path = db_path
        self.model = None
        self.encoders = {}
        
    def get_raw_data(self):
        conn = sqlite3.connect(self.db_path)
        query = '''
        SELECT 
            p.id as part_id,
            p.posicion,
            p.mandil,
            c.id as caballo_id,
            c.nombre as caballo,
            j.id as jinete_id,
            j.nombre as jinete,
            jor.fecha,
            h.id as hipodromo_id,
            car.distancia,
            car.tipo,
            car.pista,
            car.numero as nro_carrera,
            car.id as carrera_id
        FROM participaciones p
        JOIN carreras car ON p.carrera_id = car.id
        JOIN jornadas jor ON car.jornada_id = jor.id
        JOIN hipodromos h ON jor.hipodromo_id = h.id
        JOIN caballos c ON p.caballo_id = c.id
        JOIN jinetes j ON p.jinete_id = j.id
        ORDER BY jor.fecha ASC
        '''
        df = pd.read_sql(query, conn)
        conn.close()
        return df

    def feature_engineering(self, df):
        # Sort by date to calculate historical stats
        df['fecha'] = pd.to_datetime(df['fecha'])
        df = df.sort_values('fecha')
        
        # Calculate rolling stats for Jockeys
        # We need to do this carefully to avoid data leakage (using future results)
        # For a simple approach, we can use expanding window
        
        # Helper to calculate win rate
        def calculate_win_rate(series):
            wins = (series == 1).sum()
            total = len(series)
            return wins / total if total > 0 else 0

        # This is slow in pandas for large datasets, but fine for now
        # A faster way is to group by ID and shift
        
        # 1. Jockey Stats
        # Create a dummy column for 'is_win'
        df['is_win'] = (df['posicion'] == 1).astype(int)
        df['is_top3'] = (df['posicion'] <= 3).astype(int)
        
        # Group by Jockey and calculate expanding mean (shifted by 1 to exclude current race)
        df['jockey_prev_wins'] = df.groupby('jinete_id')['is_win'].transform(lambda x: x.shift().expanding().sum())
        df['jockey_prev_races'] = df.groupby('jinete_id')['is_win'].transform(lambda x: x.shift().expanding().count())
        df['jockey_win_rate'] = df['jockey_prev_wins'] / df['jockey_prev_races'].replace(0, 1)
        
        # 2. Horse Stats
        df['horse_prev_wins'] = df.groupby('caballo_id')['is_win'].transform(lambda x: x.shift().expanding().sum())
        df['horse_prev_races'] = df.groupby('caballo_id')['is_win'].transform(lambda x: x.shift().expanding().count())
        df['horse_win_rate'] = df['horse_prev_wins'] / df['horse_prev_races'].replace(0, 1)
        
        df['horse_prev_top3'] = df.groupby('caballo_id')['is_top3'].transform(lambda x: x.shift().expanding().sum())
        df['horse_top3_rate'] = df['horse_prev_top3'] / df['horse_prev_races'].replace(0, 1)
        
        # Fill NaNs (first races)
        df = df.fillna(0)
        
        # Encode categorical variables
        le_pista = LabelEncoder()
        df['pista_encoded'] = le_pista.fit_transform(df['pista'].astype(str))
        self.encoders['pista'] = le_pista
        
        # Features
        features = [
            'jockey_win_rate', 'jockey_prev_races',
            'horse_win_rate', 'horse_top3_rate', 'horse_prev_races',
            'mandil', 'distancia', 'pista_encoded'
        ]
        
        # Handle missing distance
        df['distancia'] = pd.to_numeric(df['distancia'], errors='coerce').fillna(1000)
        
        return df, features

    def train(self):
        print("Cargando datos...")
        df = self.get_raw_data()
        
        if df.empty:
            print("No hay datos suficientes.")
            return
            
        print(f"Datos cargados: {len(df)} registros.")
        
        print("Generando features...")
        df_processed, feature_cols = self.feature_engineering(df)
        
        # Target: 1 if winner, 0 otherwise
        X = df_processed[feature_cols]
        y = df_processed['is_win']
        
        # Split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, shuffle=False) # Time series split
        
        print("Entrenando modelo...")
        self.model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, class_weight='balanced')
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        print("Reporte de Clasificación:")
        print(classification_report(y_test, y_pred))
        
        # Save
        if not os.path.exists('src/models'):
            os.makedirs('src/models')
            
        joblib.dump(self.model, 'src/models/rf_model_v2.pkl')
        joblib.dump(self.encoders, 'src/models/encoders_v2.pkl')
        print("Modelo guardado en src/models/rf_model_v2.pkl")
        
        # Feature Importance
        importances = pd.DataFrame({
            'feature': feature_cols,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        print("\nImportancia de Features:")
        print(importances)

if __name__ == "__main__":
    learner = HipicaLearner()
    learner.train()
