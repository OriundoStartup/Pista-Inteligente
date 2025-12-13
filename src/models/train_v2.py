import sqlite3
import pandas as pd
import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score
import joblib
import os
from .features import FeatureEngineering

class HipicaLearner:
    def __init__(self, db_path='data/db/hipica_data.db'):
        self.db_path = db_path
        self.model = None
        self.fe = FeatureEngineering()
        
    def get_raw_data(self):
        conn = sqlite3.connect(self.db_path)
        # Included 'peso' in query if not already there, 
        # but wait, the original query had peso_fs. FeatureEngineering expects 'peso_fs' to convert to 'peso'.
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

    def train(self):
        print("🚀 Iniciando Entrenamiento Avanzado (V3 - HistGradientBoosting)...")
        df = self.get_raw_data()
        
        if len(df) < 100:
            print("❌ Muy pocos datos para entrenar (min 100).")
            return
            
        print(f"📊 Dataset: {len(df)} registros.")
        
        # 1. Feature Engineering
        print("🛠️  Generando características...")
        self.fe.fit(df) # Fit encoders/imputers
        df_proc = self.fe.transform(df, is_training=True)
        
        # Add target back for splitting (transform return X df only)
        # We need y. 'is_win' is calculated inside transform but only X returned.
        # Ideally transform should handle this or we reconstruct y.
        # Re-calculating y is cheap.
        y = (df['posicion'] == 1).astype(int)
        # Align index
        y = y.loc[df_proc.index]
        
        # Filter valid rows (some might be dropped if lag creation failed weirdly, but usually fillna handles it)
        # Actually transform returns same index.
        
        X = df_proc
        
        # Time Series Split
        total = len(X)
        split_idx = int(total * 0.8)
        
        X_train = X.iloc[:split_idx]
        y_train = y.iloc[:split_idx]
        X_test = X.iloc[split_idx:]
        y_test = y.iloc[split_idx:]
        
        print("🧠 Entrenando HistGradientBoosting...")
        self.model = HistGradientBoostingClassifier(
            max_iter=200,
            max_depth=10,
            learning_rate=0.05,
            early_stopping=True,
            random_state=42,
            class_weight='balanced'
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
            
        # Feature Importance (Permutation default or built-in for HGB depends on version, HGB doesn't have feature_importances_ attr directly in older sklearn)
        # We'll skip printing feature importance for HGB to avoid version errors or use permutation_importance if needed.
        # For now, just save.
        
        # Save
        print("\n💾 Guardando artefactos...")
        os.makedirs('src/models', exist_ok=True)
        joblib.dump(self.model, 'src/models/rf_model_v2.pkl') # Keep name for compatibility or update? 
        # Plan said update data_manager, so I should probably update filename to match new model type?
        # But data_manager looks for rf_model_v2.pkl. Let's keep the name distinct if we can, or overwrite.
        # To avoid confusion, I'll name it 'model_v3.pkl' or overwrite 'rf_model_v2.pkl' but it's not RF anymore.
        # Let's overwrite 'rf_model_v2.pkl' so I don't break data_manager before I fix it?
        # No, I am tasked to fix data_manager too. I will use 'gb_model_v3.pkl'.
        
        joblib.dump(self.model, 'src/models/gb_model_v3.pkl')
        self.fe.save('src/models/feature_eng_v2.pkl')
        
        print("✅ Modelo V3 + Features Guardados.")

if __name__ == "__main__":
    learner = HipicaLearner()
    learner.train()

