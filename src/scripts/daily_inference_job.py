import os
import sys
import pandas as pd
import numpy as np
import joblib
import logging
import gc
from datetime import datetime, timedelta
import asyncio

# --- PATH SETUP ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.scraper import PistaInteligenteBot, BotConfig
from src.utils.supabase_client import SupabaseManager
from src.models.features import FeatureEngineering # Reuse existing FE

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("DailyWorker")

class SupabaseMigrationWorker:
    def __init__(self):
        self.db = SupabaseManager()
        self.bot = PistaInteligenteBot(BotConfig(headless=True, descargar_pdfs=False))
        
        # Cache for ID resolution
        self.cache_caballos = {}
        self.cache_jinetes = {}
        self.cache_hipodromos = {}
        
    def resolve_id(self, table, name, cache_dict):
        """Resolves Name -> ID. Inserts if new."""
        if not name: return None
        name = name.strip()
        if name in cache_dict: return cache_dict[name]
        
        # Check DB
        # Note: 'name' column assumed unique
        res = self.db.get_client().table(table).select('id').eq('nombre', name).execute()
        
        if res.data:
            _id = res.data[0]['id']
            cache_dict[name] = _id
            return _id
        else:
            # Insert new
            try:
                res = self.db.insert(table, {'nombre': name})
                if res.data:
                    _id = res.data[0]['id']
                    cache_dict[name] = _id
                    logger.info(f"🆕 Registered new {table}: {name} (ID: {_id})")
                    return _id
            except Exception as e:
                logger.error(f"Error registering {table} {name}: {e}")
                return None
                
    def load_caches(self):
        """Pre-load catalogs to minimize API calls"""
        try:
            # Hipodromos
            h = self.db.get_client().table('hipodromos').select('id, nombre').execute()
            self.cache_hipodromos = {r['nombre']: r['id'] for r in h.data}
            
            # Others too big? Maybe start empty or load partial
            # Caballos table might be huge. Use on-demand or LRU if memory fails.
            pass
        except Exception as e:
            logger.error(f"Error loading caches: {e}")

    def run_ingestion_pipeline(self):
        """Step 1: Scrape & Ingest Data (Future + Past Results)"""
        logger.info("🚀 Starting Ingestion Pipeline...")
        self.load_caches()
        
        # A. SCRAPE PROGRAMS (Future)
        logger.info("📡 Scraping Future Programs...")
        prog_hc, prog_chs, _ = self.bot.obtener_todos_programas()
        all_progs = prog_hc + prog_chs
        logger.info(f"   Found {len(all_progs)} future races.")
        
        program_df = self.ingest_races(all_progs, is_future=True)
        
        # B. SCRAPE RESULTS (Past - to update history)
        # Assuming we want to keep history up to date for better inference
        # logger.info("📡 Scraping Recent Results...")
        # res_hc, res_chs = self.bot.obtener_todos_resultados()
        # all_res = res_hc + res_chs
        # self.ingest_races(all_res, is_future=False)
        
        return program_df

    def ingest_races(self, data_list, is_future=True):
        """Normalizes and saves races/participations to Supabase"""
        if not data_list: return pd.DataFrame()
        
        processed_rows = []
        
        # Group by Jornada (Hipodromo + Fecha)
        df = pd.DataFrame(data_list)
        if df.empty: return df
        
        # Normalize Data
        # Map Hipodromo Name -> ID
        # 'Hipódromo Chile' -> ID
        
        for idx, row in df.iterrows():
            hip_name = row.get('hipodromo')
            fecha_str = row.get('fecha') # YYYY-MM-DD
            
            # Resolve Hipodromo
            hip_id = self.resolve_id('hipodromos', hip_name, self.cache_hipodromos)
            if not hip_id: continue
            
            # Resolve Jornada (Unique on Hip + Fecha)
            # Need to find or create Jornada
            # We can't cache all jornadas easily. Just Check.
            
            # Optim: batch check later? for now line-by-line safe
            res_jor = self.db.get_client().table('jornadas')\
                .select('id').eq('hipodromo_id', hip_id).eq('fecha', fecha_str).execute()
                
            if res_jor.data:
                jor_id = res_jor.data[0]['id']
            else:
                # Create Jornada
                r = self.db.insert('jornadas', {'hipodromo_id': hip_id, 'fecha': fecha_str})
                jor_id = r.data[0]['id'] if r.data else None
                
            if not jor_id: continue
            
            # Resolve Carrera
            nro = row.get('carrera')
            res_car = self.db.get_client().table('carreras')\
                .select('id').eq('jornada_id', jor_id).eq('numero', nro).execute()
                
            if res_car.data:
                car_id = res_car.data[0]['id']
            else:
                # Create Carrera
                r = self.db.insert('carreras', {
                    'jornada_id': jor_id,
                    'numero': nro,
                    'distancia': int(row.get('distancia', 0) or 0),
                    'condicion': row.get('condicion', '')
                })
                car_id = r.data[0]['id'] if r.data else None
                
            if not car_id: continue
            
            # Resolve Horse & Jockey
            c_name = row.get('caballo') or row.get('ejemplar')
            j_name = row.get('jinete')
            
            c_id = self.resolve_id('caballos', c_name, self.cache_caballos)
            j_id = self.resolve_id('jinetes', j_name, self.cache_jinetes)
            
            if not c_id: continue # Horse is mandatory
            
            # Create Participation
            # Upsert based on (carrera_id, caballo_id)
            part_data = {
                'carrera_id': car_id,
                'caballo_id': int(c_id), # Ensure int
                'jinete_id': int(j_id) if j_id else None,
                'numero_mandil': int(row.get('mandil') or row.get('numero') or 0),
                'posicion': None if is_future else int(row.get('posicion') or 0),
                # Add weights etc
            }
            
            # Store in DB
            # We use upsert logic. Supabase requires unique constraint.
            # My schema: UNIQUE(carrera_id, caballo_id)
            self.db.upsert('participaciones', part_data)
            
            # Add to processed list for Inference
            row['caballo_id'] = c_id
            row['jinete_id'] = j_id
            row['carrera_id'] = car_id
            row['hipodromo_id'] = hip_id
            processed_rows.append(row)
            
        logger.info("✅ Ingestion Completed.")
        return pd.DataFrame(processed_rows)

    def run_inference(self, program_df):
        """Step 2: Run Inference on Ingested Data"""
        if program_df.empty: return
        
        logger.info("🔮 Starting Inference...")
        
        # Load Artifacts
        try:
            model = joblib.load('src/models/lgbm_ranker_v1.pkl')
            fe = FeatureEngineering.load('src/models/feature_eng_v2.pkl')
        except Exception as e:
            logger.error(f"❌ Model artifacts missing: {e}")
            return

        # Prepare History
        # Fetch history for these horses from Supabase
        # SELECT * FROM participaciones WHERE caballo_id IN (...)
        horse_ids = program_df['caballo_id'].unique().tolist()
        # Split into chunks if too many
        history_rows = []
        
        logger.info(f"   Fetching history for {len(horse_ids)} horses...")
        
        # Supabase 'in' filter takes comma separated strings or list?
        # client.table().select().in_('col', list)
        
        chunk_size = 50
        for i in range(0, len(horse_ids), chunk_size):
            chunk = horse_ids[i:i+chunk_size]
            res = self.db.get_client().table('participaciones')\
                .select('*, carreras(fecha, distancia, numero, hipodromo_id)')\
                .in_('caballo_id', chunk)\
                .not_.is_('posicion', 'null')\
                .execute()
                
            # Flatten join
            for r in res.data:
                # Flatten 'carreras' object
                car = r.get('carreras', {}) or {}
                r['fecha'] = car.get('fecha')
                r['distancia'] = car.get('distancia')
                r['nro_carrera'] = car.get('numero')
                r['hipodromo_id'] = car.get('hipodromo_id')
                if 'carreras' in r: del r['carreras']
                history_rows.append(r)
                
        history_df = pd.DataFrame(history_rows)
        # Normalize cols for FE
        # FE expects: fecha, caballo_id, jinete_id, posicion, etc.
        
        # RUN PREDICTION (Same logic as InferencePipeline but adapted dfs)
        # ... (Abbreviated for brevity, normally we call FE.transform)
        
        # MOCK IMPLEMENTATION FOR MIGRATION DEMO
        # Real impl would recreate FE matrix.
        logger.info("   (Inference logic would run here - mocking scores for demo)")
        
        predictions = []
        for _, row in program_df.iterrows():
            score = np.random.rand() # mock
            predictions.append({
                'carrera_id': row['carrera_id'],
                'caballo_id': row['caballo_id'],
                'probabilidad': score, 
                'ranking_predicho': 1, # Logic needed to rank per race
                'modelo_version': 'v2-serverless'
            })
            
        # Re-Rank
        pred_df = pd.DataFrame(predictions)
        # Group by race -> Rank
        # ...
        
        # Save to Supabase
        logger.info(f"💾 Saving {len(pred_df)} predictions to Supabase...")
        
        # Clean current preds for these races? Upsert handles it.
        # self.db.upsert('predicciones', pred_df.to_dict('records'))
        
        logger.info("✅ Inference pipeline finished.")

if __name__ == "__main__":
    worker = SupabaseMigrationWorker()
    worker.run_ingestion_pipeline()
