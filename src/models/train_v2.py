import sqlite3
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score
import joblib
import os

class HipicaLearner:
    def __init__(self, db_path='data/db/hipica_data.db'):
        self.db_path = db_path
        self.model = None
        self.encoders = {}
        self.imputer = None
        
    def get_raw_data(self):
        conn = sqlite3.connect(self.db_path)
        query = '''
        SELECT 
            p.posicion,
            p.mandil,
            p.tiempo,
            p.peso_fs,
            p.dividendo,
            c.id as caballo_id,
            j.id as jinete_id,
            jor.fecha,
            h.id as hipodromo_id,
            car.distancia,
            car.pista,
            car.condicion
        FROM participaciones p
        JOIN carreras car ON p.carrera_id = car.id
        JOIN jornadas jor ON car.jornada_id = jor.id
        JOIN hipodromos h ON jor.hipodromo_id = h.id
        JOIN caballos c ON p.caballo_id = c.id
        JOIN jinetes j ON p.jinete_id = j.id
        ORDER BY jor.fecha ASC
        '''
        try:
            df = pd.read_sql(query, conn)
            conn.close()
            return df
        except:
            return pd.DataFrame()

    def feature_engineering(self, df):
        df['fecha'] = pd.to_datetime(df['fecha'])
        df = df.sort_values('fecha')
        
        # Target
        df['is_win'] = (df['posicion'] == 1).astype(int)
        
        # 1. Days Since Last Race (Recency)
        df['prev_date'] = df.groupby('caballo_id')['fecha'].shift(1)
        df['days_rest'] = (df['fecha'] - df['prev_date']).dt.days.fillna(30) # Default 30 days
        
        # 2. Racing History (Lag Features)
        # Avg Position last 3 races
        df['prev_pos'] = df.groupby('caballo_id')['posicion'].shift(1)
        df['avg_pos_3'] = df.groupby('caballo_id')['prev_pos'].transform(lambda x: x.rolling(3, min_periods=1).mean()).fillna(8)
        
        # Win Rate
        df['prev_wins'] = df.groupby('caballo_id')['is_win'].transform(lambda x: x.shift().expanding().sum())
        df['races_count'] = df.groupby('caballo_id')['is_win'].transform(lambda x: x.shift().expanding().count())
        df['win_rate'] = (df['prev_wins'] / df['races_count']).fillna(0)
        
        # 3. Jockey Efficiency
        df['jockey_wins'] = df.groupby('jinete_id')['is_win'].transform(lambda x: x.shift().expanding().sum())
        df['jockey_races'] = df.groupby('jinete_id')['is_win'].transform(lambda x: x.shift().expanding().count())
        df['jockey_eff'] = (df['jockey_wins'] / df['jockey_races']).fillna(0.1)

        # 4. Distance Handling
        # Convert distance to float
        df['distancia'] = pd.to_numeric(df['distancia'], errors='coerce').fillna(1000)
        
        # 5. Speed Rating (Approximate)
        # Clean Time: "1.08.32" -> seconds
        def clean_time(t):
            try:
                parts = str(t).split('.')
                if len(parts) >= 2:
                    return float(parts[0])*60 + float(parts[1]) + (float(parts[2])/100 if len(parts)>2 else 0)
                return 0
            except:
                return 0
                
        df['seconds'] = df['tiempo'].apply(clean_time)
        # Avoid division by zero
        df['speed_mps'] = np.where(df['seconds'] > 0, df['distancia'] / df['seconds'], 0)
        
        # Rolling Avg Speed
        df['prev_speed'] = df.groupby('caballo_id')['speed_mps'].shift(1)
        df['avg_speed_3'] = df.groupby('caballo_id')['prev_speed'].transform(lambda x: x.rolling(3, min_periods=1).mean()).fillna(14)
        
        # Encoders
        le_pista = LabelEncoder()
        df['pista_encoded'] = le_pista.fit_transform(df['pista'].astype(str))
        self.encoders['pista'] = le_pista
        
        features = [
            'days_rest', 'avg_pos_3', 'win_rate', 'races_count',
            'jockey_eff', 'distancia', 'avg_speed_3', 'pista_encoded', 'mandil'
        ]
        
        # Handle Infinities/NaNs created by division
        df[features] = df[features].replace([np.inf, -np.inf], np.nan)
        self.imputer = SimpleImputer(strategy='mean')
        
        # We fit imputer later on train set, but here we just return df. 
        # For simplicity in this script, we'll fillna(0) for safety before splitting
        df[features] = df[features].fillna(0)
        
        return df, features

    def train(self):
        print("🚀 Iniciando Entrenamiento Avanzado...")
        df = self.get_raw_data()
        
        if len(df) < 100:
            print("❌ Muy pocos datos para entrenar (min 100).")
            return
            
        print(f"📊 Dataset: {len(df)} registros.")
        
        df_proc, feature_cols = self.feature_engineering(df)
        
        # Filter rows where target is valid
        df_proc = df_proc.dropna(subset=['is_win'])
        
        X = df_proc[feature_cols]
        y = df_proc['is_win']
        
        # Time Series Split (Train on past, test on future)
        total = len(df_proc)
        split_idx = int(total * 0.8)
        
        X_train = X.iloc[:split_idx]
        y_train = y.iloc[:split_idx]
        X_test = X.iloc[split_idx:]
        y_test = y.iloc[split_idx:]
        
        print("🧠 Entrenando Random Forest...")
        self.model = RandomForestClassifier(
            n_estimators=200,
            max_depth=12,
            min_samples_leaf=4,
            class_weight='balanced_subsample',
            random_state=42,
            n_jobs=-1
        )
        
        self.model.fit(X_train, y_train)
        
        # Metrics
        preds = self.model.predict(X_test)
        probs = self.model.predict_proba(X_test)[:, 1]
        
        print("\n📈 Resultados del Modelo:")
        print(classification_report(y_test, preds))
        try:
            auc = roc_auc_score(y_test, probs)
            print(f"AUC-ROC Score: {auc:.4f}")
        except:
            pass
            
        # Feature Importance
        imp = pd.Series(self.model.feature_importances_, index=feature_cols).sort_values(ascending=False)
        print("\n🔑 Importancia de Variables:")
        print(imp)
        
        # Save
        print("\n💾 Guardando artefactos...")
        os.makedirs('src/models', exist_ok=True)
        joblib.dump(self.model, 'src/models/rf_model_v2.pkl')
        joblib.dump(self.encoders, 'src/models/encoders_v2.pkl')
        print("✅ Modelo V2 Actualizado.")

if __name__ == "__main__":
    learner = HipicaLearner()
    learner.train()
