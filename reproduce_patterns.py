import sys
import os
import json

# Add src to path to import data_manager
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.models.data_manager import calcular_todos_patrones, detectar_patrones_futuros

def reproduce():
    print("🔍 Generando Patrones...")
    patrones = calcular_todos_patrones()
    print(f"   • Total Patrones Históricos: {len(patrones)}")
    
    # Check for duplicate Signatures in output
    sigs = [str(p['signature']) for p in patrones]
    if len(sigs) != len(set(sigs)):
        print("❌ DUPLICATE SIGNATURES DETECTED IN PATRONES LIST!")
    else:
        print("✅ Patrones (Signatures): Unique")

    # Check details inside first pattern
    if patrones:
        p0 = patrones[0]
        print(f"   • Top Pattern: {p0['signature']} (Veces: {p0['veces']})")
        detalles = p0['detalle']
        print(f"   • Detalles count: {len(detalles)}")
        
        # Check duplicate details
        fechas = [d['fecha'] for d in detalles]
        if len(fechas) != len(set(fechas)):
             print("❌ DUPLICATE DATES IN PATTERN DETAILS!")
             from collections import Counter
             print(Counter(fechas))
        else:
             print("✅ Pattern Details (Fechas): Unique")

    print("\n🔍 Detectando Alertas Futuras...")
    # Mocking program loading inside? No, detecting_patrones_futuros calls obtener_analisis_jornada
    # We rely on existing logic.
    try:
        alertas = detectar_patrones_futuros()
        print(f"   • Total Alertas: {len(alertas)}")
        
        # Check duplicate alerts (same race, same pattern type)
        alert_sigs = []
        for a in alertas:
             sig = f"{a['fecha_carrera']}-{a['nro_carrera']}-{a['tipo_patron']}-{tuple(a['caballos_involucrados'])}"
             alert_sigs.append(sig)
             
        if len(alert_sigs) != len(set(alert_sigs)):
             print("❌ DUPLICATE ALERTS DETECTED!")
             from collections import Counter
             print(Counter(alert_sigs))
        else:
             print("✅ Alertas: Unique")
             
    except Exception as e:
        print(f"⚠️ Error running detector: {e}")

if __name__ == "__main__":
    reproduce()
