
import sys
import pandas as pd
# Fix for windows unicode
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from src.models.data_manager import obtener_patrones_la_tercera, obtener_analisis_jornada, obtener_estadisticas_generales


def debug_system():
    print("\n" + "="*50)
    print("--- 1. Testing Patterns (500 Error Source) ---")
    try:
        res = obtener_patrones_la_tercera()
        print(f"Result Type: {type(res)}")
        if isinstance(res, tuple):
             print(f"Tuple Length: {len(res)}")
             patrones, last_updated = res
             print(f"Patrones Count: {len(patrones) if patrones else 'None'}")
             print(f"Timestamp: '{last_updated}'")
             
             if patrones is None:
                 print("❌ ERROR: Patrones is None!")
             else:
                 print("✅ Patrones is valid iterable.")
        else:
             print(f"❌ ERROR: Expected tuple, got {type(res)}")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"❌ Exception in obtener_patrones: {e}")

    print("\n" + "="*50)
    print("--- 2. Testing Program (Missing Horses) ---")
    try:
        analisis = obtener_analisis_jornada()
        print(f"Analisis Type: {type(analisis)}")
        print(f"Total Races Found: {len(analisis)}")
        
        # Check specific date 2025-12-18
        races_18 = [r for r in analisis if r.get('fecha') == '2025-12-18']
        if races_18:
            print(f"✅ Found {len(races_18)} races for 2025-12-18")
            first_race = races_18[0]
            caballos = first_race.get('caballos')
            
            if isinstance(caballos, pd.DataFrame):
                print("Caballos is DataFrame. Columns:", caballos.columns.tolist())
                print("First row data:")
                print(caballos.iloc[0].to_dict())
                
                # Check for empty strings in name
                name_col = 'Caballo' if 'Caballo' in caballos.columns else 'nombre'
                name_val = caballos.iloc[0][name_col]
                print(f"Name Value: '{name_val}'")
                
                if not name_val or name_val.strip() == "":
                    print("❌ ERROR: Horse name is empty string!")
            else:
                 print(f"Caballos is {type(caballos)}")
                 print(caballos[0])
        else:
            print("⚠️ No races found for 2025-12-18. Available dates:")
            dates = set(r.get('fecha') for r in analisis)
            print(dates)

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"❌ Exception in obtener_analisis: {e}")

    print("\n" + "="*50)
    print("--- 3. Testing Statistics ---")

    try:
        stats = obtener_estadisticas_generales()
        print(f"Stats Keys: {stats.keys()}")
        print(f"Total Carreras: {stats.get('total_carreras')}")
    except Exception as e:
        print(f"❌ Exception in stats: {e}")

if __name__ == "__main__":
    debug_system()
