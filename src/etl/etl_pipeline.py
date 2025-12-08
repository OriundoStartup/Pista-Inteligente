# -*- coding: utf-8 -*-
"""
NORMALIZADOR Y VOLCADO DE DATOS - PISTA INTELIGENTE V4 (OPTIMIZADO)
===================================================================
Procesa los CSV exportados por el scraper y los normaliza a 3NF.
OPTIMIZACIONES:
- Caching en memoria de entidades (Caballos, Jinetes, Studs).
- Inserciones masivas (Bulk Inserts) con executemany.
- Manejo transaccional eficiente.

Autor: Oriundo Startup Chile
Versión: 4.0
"""

import sqlite3
import pandas as pd
import glob
import os
import re
from datetime import datetime
from typing import Optional, Dict, List, Tuple, Set

# Path relativo para que funcione desde cualquier ubicación del proyecto
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'hipica_data.db')

# ============================================================================
# UTILIDADES DE LIMPIEZA
# ============================================================================

class DataCleaner:
    """Herramientas para limpiar y normalizar datos (Estático)"""
    
    @staticmethod
    def clean_text(text) -> Optional[str]:
        if pd.isna(text) or text is None:
            return None
        text = str(text).strip()
        text = re.sub(r'\s+', ' ', text)
        return text if text else None
    
    @staticmethod
    def clean_numero(value) -> Optional[int]:
        if pd.isna(value) or value is None:
            return None
        try:
            if isinstance(value, str):
                match = re.search(r'(\d+)', value)
                if match:
                    return int(match.group(1))
            return int(float(value))
        except:
            return None
    
    @staticmethod
    def clean_decimal(value) -> Optional[float]:
        if pd.isna(value) or value is None:
            return None
        try:
            if isinstance(value, str):
                value = value.replace(',', '.')
                match = re.search(r'(\d+\.?\d*)', value)
                if match:
                    return float(match.group(1))
            return float(value)
        except:
            return None
    
    @staticmethod
    def clean_tiempo(tiempo_str) -> Optional[str]:
        if pd.isna(tiempo_str) or not tiempo_str:
            return None
        tiempo = DataCleaner.clean_text(tiempo_str)
        if tiempo and re.match(r'\d+:\d+', tiempo):
            return tiempo
        return None
    
    @staticmethod
    def clean_fecha(fecha_str) -> Optional[str]:
        if pd.isna(fecha_str) or not fecha_str:
            return None
        fecha_str = str(fecha_str).strip()
        if re.match(r'\d{4}-\d{2}-\d{2}', fecha_str):
            return fecha_str
        match = re.match(r'(\d{1,2})/(\d{1,2})/(\d{4})', fecha_str)
        if match:
            dia, mes, ano = match.groups()
            return f"{ano}-{int(mes):02d}-{int(dia):02d}"
        return None

# ============================================================================
# SMART LOADER (REDIS-LIKE CACHE IN MEMORY)
# ============================================================================

class SmartLoader:
    """Gestiona caches en memoria para evitar SELECTs repetitivos"""
    
    def __init__(self, conn):
        self.conn = conn
        self.cursor = conn.cursor()
        
        # Caches: {nombre_normalizado: id}
        self.caballos = {}
        self.jinetes = {}
        self.studs = {}
        self.hipodromos = {}
        
        # New items to insert: [nombre]
        self.new_caballos = set()
        self.new_jinetes = set()
        self.new_studs = set()
        
        print("🧠 Inicializando SmartLoader (Cargando datos en memoria)...")
        self._load_caches()
        
    def _load_caches(self):
        """Carga datos existentes en memoria"""
        # Hipódromos
        for id_, nombre in self.cursor.execute("SELECT id, nombre FROM hipodromos"):
            self.hipodromos[nombre.upper()] = id_
            
        # Caballos
        for id_, nombre in self.cursor.execute("SELECT id, nombre FROM caballos"):
            self.caballos[nombre.upper()] = id_
            
        # Jinetes
        for id_, nombre in self.cursor.execute("SELECT id, nombre FROM jinetes"):
            self.jinetes[nombre.upper()] = id_
            
        # Studs
        try:
            for id_, nombre in self.cursor.execute("SELECT id, nombre FROM studs"):
                self.studs[nombre.upper()] = id_
        except sqlite3.OperationalError:
            pass # Tabla studs puede no existir aun
            
        print(f"   • {len(self.caballos)} caballos cargados")
        print(f"   • {len(self.jinetes)} jinetes cargados")
        
    def resolve_hipodromo(self, nombre, codigo=None):
        if not nombre: return None
        key = nombre.upper()
        if key in self.hipodromos:
            return self.hipodromos[key]
        
        # Crear hipódromo inmediatamente (son pocos)
        self.cursor.execute("INSERT INTO hipodromos (nombre, codigo) VALUES (?, ?)", (nombre, codigo))
        new_id = self.cursor.lastrowid
        self.hipodromos[key] = new_id
        return new_id

    def register_caballo(self, nombre):
        if not nombre: return None
        key = nombre.strip().upper()
        if key not in self.caballos:
            self.new_caballos.add(key)
            return None # ID será resuelto post-inserción
        return self.caballos[key]
        
    def register_jinete(self, nombre):
        if not nombre: return None
        key = nombre.strip().upper()
        if key not in self.jinetes:
            self.new_jinetes.add(key)
            return None
        return self.jinetes[key]
    
    def register_stud(self, nombre):
        if not nombre: return None
        key = nombre.strip().upper()
        if key not in self.studs:
            self.new_studs.add(key)
            return None
        return self.studs[key]

    def flush_new_entities(self):
        """Inserta masivamente las nuevas entidades y actualiza cache"""
        if self.new_caballos:
            data = [(name,) for name in self.new_caballos]
            self.cursor.executemany("INSERT OR IGNORE INTO caballos (nombre) VALUES (?)", data)
            # Recargar cache parcial o total (simple strategy: query new ones)
            # Para simplicidad y robustez, recargamos todo selectivo podría ser complejo por IDs
            for id_, nombre in self.cursor.execute("SELECT id, nombre FROM caballos WHERE id > ?", (max(self.caballos.values(), default=0),)):
                 self.caballos[nombre.upper()] = id_
            self.new_caballos.clear()
            print(f"   ↳ {len(data)} caballos nuevos guardados.")

        if self.new_jinetes:
            data = [(name,) for name in self.new_jinetes]
            self.cursor.executemany("INSERT OR IGNORE INTO jinetes (nombre) VALUES (?)", data)
            for id_, nombre in self.cursor.execute("SELECT id, nombre FROM jinetes WHERE id > ?", (max(self.jinetes.values(), default=0),)):
                 self.jinetes[nombre.upper()] = id_
            self.new_jinetes.clear()
            print(f"   ↳ {len(data)} jinetes nuevos guardados.")
            
        if self.new_studs:
            data = [(name,) for name in self.new_studs]
            self.cursor.executemany("INSERT OR IGNORE INTO studs (nombre) VALUES (?)", data)
            for id_, nombre in self.cursor.execute("SELECT id, nombre FROM studs WHERE id > ?", (max(self.studs.values(), default=0),)):
                 self.studs[nombre.upper()] = id_
            self.new_studs.clear()
            print(f"   ↳ {len(data)} studs nuevos guardados.")
            
        self.conn.commit()

# ============================================================================
# CLASE PRINCIPAL ETL
# ============================================================================

class HipicaETL:
    
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        self._init_db()
        self.loader = SmartLoader(self.conn)
        
    def _init_db(self):
        """Crea tablas optimizadas"""
        print("🛠️ Verificando esquema de base de datos...")
        
        # Opcional: Limpiar esquema antiguo para asegurar compatibilidad
        self.cursor.execute('DROP TABLE IF EXISTS programa_carreras')
        # Si queremos forzar el stud_id en participaciones, necesitamos recrearla
        # self.cursor.execute('DROP TABLE IF EXISTS participaciones') 
        # Pero esto borraría el historial si no se regenera todo.
        # Asumamos que el usuario quiere regenerar todo desde los CSVs
        self.cursor.execute('DROP TABLE IF EXISTS participaciones')
        
        # Tablas base
        self.cursor.execute('CREATE TABLE IF NOT EXISTS hipodromos (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT UNIQUE, codigo TEXT)')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS studs (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT UNIQUE)')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS caballos (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT UNIQUE, ano_nacimiento INTEGER, padre TEXT)')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS jinetes (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT UNIQUE)')
        
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS jornadas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            hipodromo_id INTEGER NOT NULL,
            reunion TEXT,
            FOREIGN KEY(hipodromo_id) REFERENCES hipodromos(id),
            UNIQUE(fecha, hipodromo_id)
        )''')
        
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS carreras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            jornada_id INTEGER NOT NULL,
            numero INTEGER NOT NULL,
            hora TEXT,
            distancia INTEGER,
            tipo TEXT,
            grado TEXT,
            condicion TEXT,
            pista TEXT,
            FOREIGN KEY(jornada_id) REFERENCES jornadas(id),
            UNIQUE(jornada_id, numero)
        )''')
        
        # Participaciones (La tabla fact principal)
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS participaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            carrera_id INTEGER NOT NULL,
            caballo_id INTEGER NOT NULL,
            jinete_id INTEGER,
            stud_id INTEGER,
            posicion INTEGER,
            peso_fs REAL,
            peso_jinete REAL,
            distancia_cpos TEXT,
            dividendo REAL,
            tiempo TEXT,
            mandil INTEGER,
            FOREIGN KEY(carrera_id) REFERENCES carreras(id),
            FOREIGN KEY(caballo_id) REFERENCES caballos(id),
            FOREIGN KEY(jinete_id) REFERENCES jinetes(id),
            FOREIGN KEY(stud_id) REFERENCES studs(id),
            UNIQUE(carrera_id, caballo_id)
        )''')
        
        # Indexes para velocidad
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_jornadas_fecha ON jornadas(fecha)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_carreras_jornada ON carreras(jornada_id)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_participaciones_caballo ON participaciones(caballo_id)')
        
        # Tabla Programa (Normalizada)
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS programa_carreras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT, hipodromo TEXT, nro_carrera INTEGER,
            hora TEXT, distancia TEXT, condicion TEXT,
            numero INTEGER, 
            caballo_id INTEGER, 
            jinete_id INTEGER, 
            stud_id INTEGER, 
            peso TEXT,
            FOREIGN KEY(caballo_id) REFERENCES caballos(id),
            FOREIGN KEY(jinete_id) REFERENCES jinetes(id),
            FOREIGN KEY(stud_id) REFERENCES studs(id),
            UNIQUE(fecha, hipodromo, nro_carrera, numero)
        )''')
        
        self.conn.commit()

    def process_csv(self, file_path):
        """Procesa un CSV eficientemente"""
        filename = os.path.basename(file_path)
        print(f"\n📄 Procesando: {filename}")
        
        # Detectar Header Row dinámicamente y leer con StringIO
        from io import StringIO
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                lines = f.readlines()
            
            header_idx = 0
            for i, line in enumerate(lines[:20]):
                if 'Carrera' in line or 'Numero' in line or 'Cab. N' in line:
                    header_idx = i
                    break
            
            # Detectar delimitador
            delimiter = ','
            if ';' in lines[header_idx]:
                delimiter = ';'
            
            # Construir CSV limpio desde el header detectado
            csv_content = "".join(lines[header_idx:])
            df = pd.read_csv(StringIO(csv_content), sep=delimiter)
            
        except Exception as e:
            print(f"❌ Error leyendo CSV: {e}")
            return

        # Detectar tipo y Metadatos del nombre del archivo
        # Formato esperado: PROGRAMA_CODIGO_YYYY-MM-DD.csv
        is_program = 'programa' in filename.lower()
        
        # Normalizar nombres de columnas (Map headers)
        # Soporta formatos CHC (Cab. N°), VSC (Numero) y HC (Carrera_Nro)
        col_map = {
            # Programas
            'Carrera': 'carrera',
            'Carrera_Nro': 'carrera',
            'carrera': 'carrera',
            'Cab. N°': 'numero',
            'Numero': 'numero',
            'Nro_Caballo': 'numero',
            'numero': 'numero',
            'Nombre Ejemplar': 'nombre',
            'Caballo': 'nombre',
            'Ejemplar': 'nombre',
            'ejemplar': 'nombre',
            'ganador': 'nombre',
            'Jinete': 'jinete',
            'jinete': 'jinete',
            'Peso': 'peso',
            'peso': 'peso',
            'peso_caballo': 'peso',
            'Condición Principal': 'condicion',
            'Condiciones': 'condicion',
            'tipo': 'condicion', # HC usa tipo
            'Distancia': 'distancia',
            'distancia': 'distancia',
            'Hora': 'hora',
            'hora': 'hora',
            'Tiempo': 'hora',
            'Haras_Stud': 'stud',
            'Stud': 'stud',
            'stud': 'stud',
            'Fecha': 'fecha',
            'fecha': 'fecha',
            
            # Resultados
            'Lugar': 'posicion',
            'posicion': 'posicion',
            'Dividendo': 'dividendo',
            'dividendo': 'dividendo',
            'Peso Jinete': 'peso_jinete',
            'peso_jinete': 'peso_jinete',
            'PF': 'peso_fisico',
            'Partida': 'mandil',
            'partida': 'mandil'
        }
        df.rename(columns=col_map, inplace=True)
        
        # Eliminar columnas duplicadas si existen
        df = df.loc[:, ~df.columns.duplicated()]

        # Mapeo de Codigos
        hipodromos_k = {
            'CHC': 'Club Hípico de Santiago',
            'CONCE': 'Club Hípico de Concepción',
            'HC': 'Hipódromo Chile',
            'VSC': 'Valparaíso Sporting',
            'CHS': 'Club Hípico de Santiago'
        }
        
        # Intentar extraer fecha e hipodromo del nombre
        match = re.search(r'_([A-Z]+)_(\d{4}-\d{2}-\d{2})', filename)
        if match:
            code, date_str = match.groups()
            full_name = hipodromos_k.get(code, code)
            
            # Sobreescribir fecha con la del archivo
            df['fecha'] = date_str
            
            # Inyectar hipodromo si falta
            if 'hipodromo' not in df.columns:
                df['hipodromo'] = full_name

        if is_program:
            self._process_program_bulk(df)
        else:
            self._process_results_bulk(df)

    def _process_program_bulk(self, df):
        """Inserción masiva de programas (Normalizados)"""
        # 1. Recolectar entidades
        processed_rows = []
        hoy = datetime.now().strftime('%Y-%m-%d')
        # self.cursor.execute("DELETE FROM programa_carreras WHERE fecha < ?", (hoy,)) # DISABLED FOR BATCH IMPORT
        
        for _, row in df.iterrows():
            item = {}
            item['fecha'] = DataCleaner.clean_fecha(row.get('fecha'))
            if not item['fecha']: continue
            
            item['hipodromo_txt'] = DataCleaner.clean_text(row.get('hipodromo'))
            item['caballo_txt'] = DataCleaner.clean_text(row.get('nombre'))
            item['jinete_txt'] = DataCleaner.clean_text(row.get('jinete'))
            item['stud_txt'] = DataCleaner.clean_text(row.get('stud'))
            
            # Registrar en loader
            self.loader.resolve_hipodromo(item['hipodromo_txt'])
            self.loader.register_caballo(item['caballo_txt'])
            self.loader.register_jinete(item['jinete_txt'])
            self.loader.register_stud(item['stud_txt'])
            
            item['raw_row'] = row # Guardar para extraer otros campos despues
            processed_rows.append(item)
            
        # 2. Sincronizar entidades
        print(f"   🌊 Sincronizando {len(processed_rows)} registros de programa...")
        self.loader.flush_new_entities()
        
        # 3. Preparar inserción
        data = []
        for item in processed_rows:
            row = item['raw_row']
            caballo_id = self.loader.register_caballo(item['caballo_txt'])
            jinete_id = self.loader.register_jinete(item['jinete_txt'])
            stud_id = self.loader.register_stud(item['stud_txt'])
            
            data.append((
                item['fecha'],
                item['hipodromo_txt'],
                DataCleaner.clean_numero(row.get('carrera')),
                DataCleaner.clean_text(row.get('hora')),
                DataCleaner.clean_text(row.get('distancia')),
                DataCleaner.clean_text(row.get('condicion')),
                DataCleaner.clean_numero(row.get('numero')),
                caballo_id,
                jinete_id,
                stud_id,
                DataCleaner.clean_text(row.get('peso'))
            ))

        if data:
            self.cursor.executemany('''
                INSERT OR REPLACE INTO programa_carreras 
                (fecha, hipodromo, nro_carrera, hora, distancia, condicion, numero, caballo_id, jinete_id, stud_id, peso)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', data)
            self.conn.commit()
            print(f"   ✅ {len(data)} registros de programa insertados.")

    def _process_results_bulk(self, df):
        """
        Proceso optimizado de resultados:
        1. Recolectar todas las entidades nuevas (Strings).
        2. Insertar entidades nuevas y actualizar Cache (SmartLoader).
        3. Resolver IDs en memoria.
        4. Insertar Estructura (Jornada -> Carrera) si no existe.
        5. Insertar Participaciones (Bulk).
        """
        
        # Paso 1: Recolección y resolución en RAM
        # Lista temporal de objetos row procesados
        processed_rows = []
        
        for _, row in df.iterrows():
            item = {}
            
            # Limpieza básica
            item['hipodromo_txt'] = DataCleaner.clean_text(row.get('hipodromo'))
            item['fecha'] = DataCleaner.clean_fecha(row.get('fecha'))
            item['carrera_nro'] = DataCleaner.clean_numero(row.get('carrera'))
            item['reunion'] = DataCleaner.clean_text(row.get('reunion'))
            
            # Determinar columnas (Ya normalizadas a 'nombre')
            item['caballo_txt'] = DataCleaner.clean_text(row.get('nombre'))
                 
            item['jinete_txt'] = DataCleaner.clean_text(row.get('jinete'))
            item['stud_txt'] = DataCleaner.clean_text(row.get('stud')) # Si existe en CSV
            
            # Datos de carrera
            item['hora'] = DataCleaner.clean_text(row.get('hora'))
            item['distancia'] = DataCleaner.clean_numero(row.get('distancia'))
            item['tipo'] = DataCleaner.clean_text(row.get('tipo'))
            item['pista'] = DataCleaner.clean_text(row.get('pista'))
            
            # Datos participación
            item['posicion'] = DataCleaner.clean_numero(row.get('posicion'))
            item['peso_fs'] = DataCleaner.clean_decimal(row.get('peso_fs'))
            item['dividendo'] = DataCleaner.clean_decimal(row.get('dividendo'))
            item['mandil'] = DataCleaner.clean_numero(row.get('mandil')) 
            
            if not item['fecha'] or not item['hipodromo_txt'] or not item['caballo_txt']:
                continue
                
            # Registrar en Loader (Solo registra intención, no inserta aun)
            self.loader.resolve_hipodromo(item['hipodromo_txt'])
            self.loader.register_caballo(item['caballo_txt'])
            self.loader.register_jinete(item['jinete_txt'])
            self.loader.register_stud(item['stud_txt'])
            
            processed_rows.append(item)
            
        # Paso 2: Flush de entidades nuevas
        print(f"   🌊 Sincronizando {len(processed_rows)} filas...")
        self.loader.flush_new_entities()
        
        # Paso 3 & 4: Estructura y Participaciones
        # Como Jornadas y Carreras dependen de la lógica de negocio (unique constraint),
        # las procesamos linealmente o con un cache local por batch.
        
        participaciones_batch = []
        
        # Cache local para IDs de Jornada/Carrera en este archivo
        # {(fecha, hip_id): jornada_id}
        local_jornadas = {}
        # {(jornada_id, nro_carrera): carrera_id}
        local_carreras = {}
        
        for item in processed_rows:
            hip_id = self.loader.resolve_hipodromo(item['hipodromo_txt'])
            caballo_id = self.loader.register_caballo(item['caballo_txt'])
            jinete_id = self.loader.register_jinete(item['jinete_txt'])
            stud_id = self.loader.register_stud(item['stud_txt'])
            
            if not hip_id or not caballo_id: 
                continue # Should not happen after flush
                
            # Resolver Jornada
            jornada_key = (item['fecha'], hip_id)
            if jornada_key not in local_jornadas:
                # Buscar o crear DB
                self.cursor.execute("SELECT id FROM jornadas WHERE fecha=? AND hipodromo_id=?", jornada_key)
                res = self.cursor.fetchone()
                if res:
                    local_jornadas[jornada_key] = res[0]
                else:
                    self.cursor.execute("INSERT INTO jornadas (fecha, hipodromo_id, reunion) VALUES (?, ?, ?)", 
                                        (*jornada_key, item['reunion']))
                    local_jornadas[jornada_key] = self.cursor.lastrowid
            jornada_id = local_jornadas[jornada_key]
            
            # Resolver Carrera
            carrera_key = (jornada_id, item['carrera_nro'])
            if carrera_key not in local_carreras:
                self.cursor.execute("SELECT id FROM carreras WHERE jornada_id=? AND numero=?", carrera_key)
                res = self.cursor.fetchone()
                if res:
                    local_carreras[carrera_key] = res[0]
                else:
                    self.cursor.execute('''INSERT INTO carreras (jornada_id, numero, hora, distancia, tipo, pista) 
                                           VALUES (?, ?, ?, ?, ?, ?)''', 
                                           (jornada_id, item['carrera_nro'], item['hora'], item['distancia'], item['tipo'], item['pista']))
                    local_carreras[carrera_key] = self.cursor.lastrowid
            carrera_id = local_carreras[carrera_key]
            
            # Agregar a batch participaciones
            participaciones_batch.append((
                carrera_id, caballo_id, jinete_id, stud_id,
                item['posicion'], item['peso_fs'], item['dividendo'], item['mandil']
            ))
            
        # Paso 5: Bulk Insert Participaciones
        if participaciones_batch:
            self.cursor.executemany('''
                INSERT OR IGNORE INTO participaciones 
                (carrera_id, caballo_id, jinete_id, stud_id, posicion, peso_fs, dividendo, mandil)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', participaciones_batch)
            self.conn.commit()
            print(f"   ✅ {len(participaciones_batch)} participaciones procesadas.")

    def run(self):
        print("🚀 Iniciando ETL Optimizado...")
        files = glob.glob('exports/*.csv')
        print(f"📂 Encontrados {len(files)} archivos CSV.")
        
        for f in files:
            self.process_csv(f)
            
        self.conn.close()
        print("🏁 ETL Completado.")

if __name__ == "__main__":
    etl = HipicaETL()
    etl.run()
