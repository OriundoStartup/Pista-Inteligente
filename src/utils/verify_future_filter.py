
import sys
import os
from datetime import datetime, timedelta

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.models.data_manager import obtener_analisis_jornada

def verify_future_filter():
    print("Running verification for future filter...")
    
    # Define today strings (Chile)
    chile_time = datetime.utcnow() - timedelta(hours=3)
    today_str = chile_time.strftime('%Y-%m-%d')
    print(f"Current Chile Date: {today_str}")

    try:
        analisis = obtener_analisis_jornada()
    except Exception as e:
        print(f"Error fetching analysis: {e}")
        return

    if not analisis:
        print("No predictions returned (cache might be empty or all past).")
        return

    fechas_encontradas = set()
    found_past = False
    
    for carrera in analisis:
        fecha = carrera.get('fecha')
        fechas_encontradas.add(fecha)
        
        if fecha < today_str:
            print(f"❌ FAIL: Found past date: {fecha}")
            found_past = True
    
    print(f"Dates found: {sorted(list(fechas_encontradas))}")
    
    if found_past:
        raise AssertionError("Found past dates in predictions!")
    else:
        print("✅ SUCCESS: All dates are >= today.")

if __name__ == "__main__":
    verify_future_filter()
