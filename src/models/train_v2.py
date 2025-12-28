import sqlite3
import pandas as pd
import numpy as np
import lightgbm as lgb
from sklearn.model_selection import GroupKFold
import joblib
import os
try:
    from src.models.features import FeatureEngineering
except ImportError:
    from features import FeatureEngineering

class HipicaLearner:
    def __init__(self, db_path='data/db/hipica_data.db'):
        self.db_path = db_path
        self.model = None
        self.fe = FeatureEngineering()
        
    def get_raw_data(self):
        conn = sqlite3.connect(self.db_path)
        # We need to sort STRICTLY by race to create groups
        # Added 'car.id as carrera_id' to identifying groups
        query = '''
        SELECT 
            p.posicion,
            p.mandil,
            p.tiempo,
            p.peso_fs,
            p.dividendo,
            c.id as caballo_id,
            c.padre,
            j.id as jinete_id,
            p.stud_id as preparador_id,
            jor.fecha,
            h.id as hipodromo_id,
            h.nombre as hipodromo_nombre,
            car.id as carrera_id,
            car.distancia,
            car.pista,
            car.condicion
        FROM participaciones p
        JOIN carreras car ON p.carrera_id = car.id
        JOIN jornadas jor ON car.jornada_id = jor.id
        JOIN hipodromos h ON jor.hipodromo_id = h.id
        JOIN caballos c ON p.caballo_id = c.id
        JOIN jinetes j ON p.jinete_id = j.id
        ORDER BY jor.fecha ASC, car.id ASC
        '''
        try:
            df = pd.read_sql(query, conn)
            conn.close()
            return df
        except:
            return pd.DataFrame()

    def train(self):
        print("🚀 Iniciando Entrenamiento V2.0 (LGBM Ranker)...")
        df = self.get_raw_data()
        
        if len(df) < 100:
            print("❌ Muy pocos datos para entrenar (min 100).")
            return
            
        print(f"📊 Dataset: {len(df)} registros.")
        
        # 1. Feature Engineering
        print("🛠️  Generando características...")
        self.fe.fit(df) 
        df_proc = self.fe.transform(df, is_training=True)
        
        # 2. Prep for Ranking
        # Target: Relevance. 
        # Win (1) = 3 relevance, Top 3 = 1, Others = 0? 
        # Or just Win=1, others=0. Lambdarank with binary target works fine (optimizes AUC/NDCG).
        # Let's try graded relevance: 1st=3, 2nd=2, 3rd=1, Rest=0
        
        # Re-attach target and group info
        df_proc['posicion'] = df['posicion']
        df_proc['carrera_id'] = df['carrera_id']
        
        # Relevance function
        def get_relevance(pos):
            if pos == 1: return 3
            if pos == 2: return 2
            if pos == 3: return 1
            return 0
            
        y = df_proc['posicion'].apply(get_relevance)
        groups = df_proc['carrera_id']
        
        # Drop non-feature cols
        X = df_proc.drop(columns=['posicion', 'carrera_id', 'is_win'], errors='ignore')
        
        # Split (Time Series Group Split manually)
        unique_groups = groups.unique()
        n_groups = len(unique_groups)
        split_idx = int(n_groups * 0.8)
        train_groups = unique_groups[:split_idx]
        test_groups = unique_groups[split_idx:]
        
        # Masks
        train_mask = groups.isin(train_groups)
        test_mask = groups.isin(test_groups)
        
        X_train, y_train = X[train_mask], y[train_mask]
        X_test, y_test = X[test_mask], y[test_mask]
        
        # Query groups for LGBM (number of items per group)
        # Note: Data MUST be sorted by group for LGBM
        # We already sorted by date/carrera_id in SQL, so it should be contiguous.
        # But let's verification sort just in case.
        # X_train is subset, preserving order.
        
        group_train = groups[train_mask].value_counts(sort=False).sort_index()
        # Wait, value_counts sorts by count or index? sort=False sorts by appearance? No.
        # Safe way: iterate unique groups in order of appearance.
        # But groups series might not be perfectly sorted if 'isin' shuffles? No, boolean mask keeps order.
        
        # Correctly building group array:
        # We need the count of rows for each distinct group ID, IN THE ORDER they appear in X.
        # Since X is sorted by query_id (carrera_id), we can just groupby(sort=False).
        
        q_train = groups[train_mask].groupby(groups[train_mask], sort=False).count()
        q_test = groups[test_mask].groupby(groups[test_mask], sort=False).count()
        
        print(f"🧠 Entrenando LGBMRanker ({len(q_train)} carreras train, {len(q_test)} carreras test)...")
        
        self.model = lgb.LGBMRanker(
            objective="lambdarank",
            metric="ndcg",
            n_estimators=500,
            learning_rate=0.05,
            num_leaves=31,
            random_state=42,
            importance_type='gain'
        )
        
        self.model.fit(
            X_train, y_train,
            group=q_train,
            eval_set=[(X_test, y_test)],
            eval_group=[q_test],
            eval_at=[1],
            callbacks=[lgb.early_stopping(stopping_rounds=50), lgb.log_evaluation(50)]
        )
        
        # Metrics manually? Early stopping does it.
        # NDCG@1 is what we care about.
        
        # Save
        print("\n💾 Guardando artefactos...")
        os.makedirs('src/models', exist_ok=True)
        # New filename v1
        joblib.dump(self.model, 'src/models/lgbm_ranker_v1.pkl')
        self.fe.save('src/models/feature_eng_v2.pkl')
        
        print("✅ Modelo Ranker V1 Guardado.")

if __name__ == "__main__":
    learner = HipicaLearner()
    learner.train()

