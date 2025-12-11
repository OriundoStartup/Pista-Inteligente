from src.models.data_manager import obtener_patrones_la_tercera, cargar_datos_3nf

# Force creating a context if needed or just calling the function
print("🔍 Checking Patterns...")
try:
    df = cargar_datos_3nf()
    print(f"📊 3NF Data Loaded: {len(df)} rows.")
    if not df.empty and 'fecha' in df.columns:
        print(f"   Dates range: {df['fecha'].min()} to {df['fecha'].max()}")
        if '2025-12-07' in df['fecha'].values:
            print("   ✅ Data for 2025-12-07 is present.")
        else:
             print("   ⚠️ Data for 2025-12-07 is MISSING in 3NF DF.")
    
    patrones = obtener_patrones_la_tercera('Todos')
    print(f"✅ Found {len(patrones)} patterns.")
    
    if len(patrones) > 0:
        print("Top 3 Patterns:")
        for p in patrones[:3]:
            print(f"Type: {p['tipo']} | Count: {p['veces']}")
            print("Detalle (First item):", p['detalle'][0])
            print("-" * 20)
    else:
        print("⚠️ No patterns found. Check if historical results are loaded in DB (fact_participaciones or 3nf view).")

except Exception as e:
    print(f"❌ Error getting patterns: {e}")
