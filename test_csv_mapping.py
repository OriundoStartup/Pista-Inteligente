import pandas as pd
import re

print("=== TEST CSV MAPPING ===")

filename = 'exports/RESULTADOS_HC_2025-12-13.csv'
print(f"📂 Leyendo: {filename}")

# Leer CSV como lo hace el ETL
try:
    df = pd.read_csv(filename)
    print(f"✅ CSV Leído. Columnas originales: {list(df.columns)}")
    print(f"🔎 Primeras filas de 'Puesto':")
    print(df['Puesto'].head())
except Exception as e:
    print(f"❌ Error leyendo CSV: {e}")
    exit()

# Simular col_map del ETL
col_map = {
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
    'tipo': 'condicion',
    'Distancia': 'distancia',
    'distancia': 'distancia',
    'Hora': 'hora',
    'hora': 'hora',
    'Tiempo': 'tiempo',
    'tiempo': 'tiempo',
    'Haras_Stud': 'stud',
    'Stud': 'stud',
    'stud': 'stud',
    'Fecha': 'fecha',
    'fecha': 'fecha',
    
    # Resultados
    'Lugar': 'posicion',
    'Puesto': 'posicion',   # <-- EL FIX
    'posicion': 'posicion',
    'Dividendo': 'dividendo',
    'dividendo': 'dividendo',
    'Peso Jinete': 'peso_jinete',
    'peso_jinete': 'peso_jinete',
    'PF': 'peso_fisico',
    'Partida': 'mandil',
    'partida': 'mandil'
}

print("\n🔄 Aplicando rename...")
df.rename(columns=col_map, inplace=True)
print(f"✅ Columnas mapeadas: {list(df.columns)}")

if 'posicion' in df.columns:
    print("\n✅ Columna 'posicion' encontrada!")
    print(df[['carrera', 'numero', 'nombre', 'posicion']].head())
    
    # Simular DataCleaner.clean_numero
    print("\n🧹 Probando limpieza de posicion...")
    def clean_numero(val):
        if val is None or pd.isna(val): return None
        s = str(val).strip()
        # Manejar 'U' u otros textos, extraer solo digitos si es posible o retornar None
        if s.isdigit(): return int(s)
        # Hack para strings '1', '2'
        try:
            return int(float(s))
        except:
            return None # Si es 'U' retorna None (o sea, no tiene posición numérica válida para ranking)
            
    df['posicion_clean'] = df['posicion'].apply(clean_numero)
    print(df[['posicion', 'posicion_clean']].head(15))
else:
    print("\n❌ Columna 'posicion' NO encontrada después del mapeo.")
