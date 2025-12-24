import pandas as pd
import numpy as np
import joblib
import os
import sqlite3
import json
import sys
from datetime import datetime
from src.models.data_manager import cargar_programa, cargar_datos_3nf
from src.models.features import FeatureEngineering

# Fix for Windows Unicode printing
if sys.platform == "win32" and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

class InferencePipeline:
    def __init__(self, model_path='src/models/lgbm_ranker_v1.pkl', fe_path='src/models/feature_eng_v2.pkl'):
        self.model_path = model_path
        self.fe_path = fe_path
        self.model = None
        self.fe = None
        self.history = None
        
    def load_artifacts(self):
        if not os.path.exists(self.model_path) or not os.path.exists(self.fe_path):
            raise FileNotFoundError("Model or FE artifact missing.")
            
        self.model = joblib.load(self.model_path)
        self.fe = FeatureEngineering.load(self.fe_path)
        print("✅ Models loaded.")
        
        # Load History for Feature Generation
        print("⏳ Loading history for features...")
        self.history = cargar_datos_3nf() 
        # Note: cargar_datos_3nf logic might need checking if it returns dataframe with expected columns
        # Assuming it does based on data_manager usage.
        
    def run(self):
        print("🚀 Starting Inference Pipeline...")
        self.load_artifacts()
        
        # 1. Load Future Races
        print("📅 Loading Future Program...")
        df_program = cargar_programa(solo_futuras=True)
        
        if df_program.empty:
            print("⚠️ No future races found in DB.")
            return
            
        # 2. Pre-process Program to match FE inputs
        # Program cols: fecha, hipodromo, nro_carrera, numero, caballo, jinete, stud, peso, distancia(maybe)
        # FE expects: fecha, caballo_id, jinete_id, preparador_id, etc.
        
        # We need to MAP names to IDs using History (or lookup tables).
        # Since program might have names not IDs if came from scraping CSVs without IDs.
        # Check `cargar_programa` -> it tries to join IDs but falls back to names if flat.
        # Inspecting `cargar_programa` output from previous steps: it returns names.
        
        # We need a robust Name->ID mapper.
        # Or `FeatureEngineering` should handle names? 
        # Current `features_v2.py` uses `caballo_id` for grouping. 
        # If we only have names, we must map them.
        
        # Helper map builder
        caballo_map = self.history[['caballo_id', 'caballo']].drop_duplicates('caballo').set_index('caballo')['caballo_id'].to_dict()
        jinete_map = self.history[['jinete_id', 'jinete']].drop_duplicates('jinete').set_index('jinete')['jinete_id'].to_dict()
        # Stud as Preparador
        # In history, we aliased stud_id as preparador_id in train_v2 logic.
        # Check history columns
        if 'stud_id' in self.history.columns:
             stud_map = self.history[['stud_id', 'stud']].drop_duplicates('stud').set_index('stud')['stud_id'].to_dict()
        else:
             stud_map = {}

        # Prepare input DataFrames
        predictions_batch = []
        
        # Group by Race to handle Softmax Context
        # Race ID = Hipodromo + Fecha + Nro_Carrera
        df_program['race_unique_id'] = df_program['fecha'].astype(str) + "_" + df_program['hipodromo'] + "_" + df_program['nro_carrera'].astype(str)
        
        mapped_rows = []
        
        print(f"🔄 Processing {len(df_program)} entries...")
        
        for idx, row in df_program.iterrows():
            # Defaults
            c_name = row.get('caballo', 'Unknown')
            j_name = row.get('jinete', 'Unknown')
            s_name = row.get('stud', 'Unknown') # stud is preparador
            
            c_id = caballo_map.get(c_name, 0) # 0 for Cold Start
            j_id = jinete_map.get(j_name, 0)
            p_id = stud_map.get(s_name, 0)
            
            # Construct row for FE
            # Note: FE expects historical context.
            # We must append this row to history of this horse to generate lags?
            # Or just pass history + current row to FE.transform?
            # FE.transform sorts by date.
            
            # Efficient approach:
            # We cannot feed 1000 future rows at once to FE and expect lags to be correct if they depend on HISTORY.
            # FE V2 `transform` takes a DF. It calculates lags using shift().
            # If we pass (History + FutureRow), it works.
            # But passing History + All Future Rows? 
            # If future rows are for same horse, shifts might grab other future rows (leakage? or just predicting sequence).
            # Usually we predict next race.
            
            # To be safe and simpler:
            # Use `analizar_probabilidad_caballos` logic style (History + 1 Current Row) per horse?
            # That is slow for batch.
            
            # OPTIMIZED BATCH:
            # 1. Create a "Current State" DF with all future rows.
            # 2. Concat History + Future.
            # 3. Sort by Date.
            # 4. Transform.
            # 5. Extract only the transformed rows corresponding to Future.
            
            # This is vectorizable!
            
            input_row = {
                'fecha': pd.to_datetime(row['fecha']),
                'caballo_id': str(c_id),
                'jinete_id': str(j_id),
                'preparador_id': str(p_id),
                'hipodromo_id': row.get('hipodromo', 'UNKNOWN'), # FE uses string
                'distancia': row.get('distancia', 1000),
                'pista': row.get('pista', 'ARENA'), # Might need robust detection if logic is complex
                'peso_fs': row.get('peso', 470),
                'mandil': row.get('numero', 0),
                'posicion': 0, # Future
                'is_win': 0,
                'tiempo': 0,
                'padre': '0' # TODOMap padre if possible from static table
            }
            # Try to get Father from History for Cold Start V2
            # We can build a map of horse_id -> padre
            # But we only have mapped c_id now.
            
            mapped_rows.append(input_row)

        df_future = pd.DataFrame(mapped_rows)
        
        # 3. Transform (Batch)
        # We need to concat history to generate features (lags, win rates)
        # history has columns: ... 
        # ensure columns match
        
        # Min cols
        cols_needed = ['fecha', 'caballo_id', 'jinete_id', 'preparador_id', 'hipodromo_id', 'distancia', 'pista', 'peso_fs', 'mandil', 'posicion', 'is_win', 'padre', 'tiempo']
        
        # Ensure history has these
        # cargar_datos_3nf output might differ from train_v2 query.
        # Let's inspect history cols in runtime or assume we need to adjust.
        # For this task, we assume history is compatible or flexible.
        # If history missing 'preparador_id', we create it.
        
        if 'preparador_id' not in self.history.columns:
            if 'stud_id' in self.history.columns:
                 self.history['preparador_id'] = self.history['stud_id']
            else:
                 self.history['preparador_id'] = '0'
                 
        if 'padre' not in self.history.columns:
            self.history['padre'] = '0'
            
        # Aliasing
        if 'peso' in self.history.columns and 'peso_fs' not in self.history.columns:
            self.history['peso_fs'] = self.history['peso']
            
        common_cols = list(set(self.history.columns) & set(cols_needed))
        
        # Concat
        print("🧠 Transforming Data (History + Future)...")
        # To avoid massive memory, filter history to relevant horses?
        # Only horses in df_future.
        relevant_horses = df_future['caballo_id'].unique()
        hist_subset = self.history[self.history['caballo_id'].isin(relevant_horses)].copy()
        
        # Keep only needed columns to save memory
        hist_subset = hist_subset[common_cols]
        
        # Filter df_future to common cols + whatever valid
        df_future_input = df_future[common_cols]
        
        # Concat
        df_combined = pd.concat([hist_subset, df_future_input], ignore_index=True)
        
        # Transform
        df_transformed = self.fe.transform(df_combined, is_training=False)
        
        # Extract Future (the last entries per horse)
        # FE transform sorts by date. Future dates are > history dates.
        # So we can just filter by date >= min(future_date)
        min_future_date = df_future['fecha'].min()
        
        # Filter transformed
        # We need to map back to original df_program rows for Race grouping (Softmax).
        # We can join by index? No, sort breaks index.
        # Join by key keys (Horse + Date)?
        
        X_future = df_transformed[df_transformed.index >= len(hist_subset)].copy() # Rough logic, indices might reset
        # Better: Filter where fecha >= min_future
        # But df_transformed doesn't have fecha? FE might drop it?
        # FE v2 returns transformed cols. We need to check if it keeps ID/Date.
        # FE v2 returns DataFrame with index of input.
        # Input was df_combined.
        # So we can use the index of df_combined rows that came from df_future.
        
        # Index range of future part: [len(hist_subset) : end]
        future_indices = range(len(hist_subset), len(df_combined))
        X_pred = df_transformed.iloc[future_indices].copy()
        
        # 4. Predict (Batch)
        print("🔮 Predicting...")
        raw_scores = self.model.predict(X_pred)
        
        # 5. Softmax & Save
        # attach scores to df_program (careful with order)
        # df_combined sorted by date? FE sorts.
        # But we extracted by index range... IF concat preserved order and FE sort didn't mix history/future for same horse...
        # FE sorts by `fecha`. Future > History. So Future rows are at the end overall? 
        # NOT NECESSARILY. If today is Monday, we predict Tuesday.
        # But we have multiple horses.
        # Sort is global by date? Yes.
        # So Future rows for all horses are at the end? Yes.
        # But mix of horses.
        
        # We need to link X_pred back to the "Race Group".
        # We can rebuild the Race ID map.
        # Extract IDs from df_combined (it was sorted inside FE? No, FE sorts a COPY. The returned DF has index of input DF?
        # Check features.py (v2): `return pd.DataFrame(..., index=df.index)`
        # YES! It preserves index.
        # So df_combined indices were 0..N-1 (History) and N..N+M (Future).
        # So `X_pred = df_transformed.iloc[future_indices]` is correct reference to Future rows (if we didn't reset index duplicates).
        
        # Attach scores
        df_program['raw_score'] = raw_scores
        
        # Apply Softmax per Race
        print("⚖️ Applying Softmax Normalization...")
        
        results = []
        
        for race_id, group in df_program.groupby('race_unique_id'):
            # Softmax
            scores = group['raw_score'].values
            exp_scores = np.exp(scores)
            probs = exp_scores / np.sum(exp_scores)
            
            # Map back
            group['prob_win'] = probs
            
            # Formating
            for idx, r in group.iterrows():
                results.append({
                    'fecha': r['fecha'], # str or date
                    'hipodromo': r['hipodromo'],
                    'carrera': r['nro_carrera'],
                    'numero': r['numero'],
                    'caballo': r['caballo'],
                    'probabilidad': round(r['prob_win'] * 100, 1)
                })
                
        # Save results
        self.save_results(results)

    def save_results(self, results):
        # Save to local JSON/DB
        path = 'data/predicciones_activas.json'
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(results, f, default=str, indent=2)
        print(f"✅ Saved {len(results)} predictions to {path}")
        
        # Optional: Save to SQLite
        try:
            df = pd.DataFrame(results)
            conn = sqlite3.connect('data/db/hipica_data.db')
            df.to_sql('predicciones_activas', conn, if_exists='replace', index=False)
            conn.close()
            print("✅ Saved to DB table 'predicciones_activas'")
        except Exception as e:
            print(f"⚠️ DB Save Error: {e}")

if __name__ == "__main__":
    pipeline = InferencePipeline()
    pipeline.run()
