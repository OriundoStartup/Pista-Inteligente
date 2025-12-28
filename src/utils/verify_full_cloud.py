
import sys
import os

# Add root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.models.data_manager import obtener_analisis_jornada

def verify_full_cloud():
    print("☁️ Verificando Arquitectura Full Cloud...")
    
    # 1. Fetch data (Should come strictly from Firestore)
    try:
        analisis = obtener_analisis_jornada(use_firestore=True)
    except Exception as e:
        print(f"❌ Error al consultar Firestore: {e}")
        return

    if not analisis:
        print("⚠️ Firestore retornó lista vacía. (Puede ser normal si no se ha migrado data nueva)")
        print("   -> Asegúrese de ejecutar: python src/utils/migrate_to_firebase.py")
        return

    print(f"✅ Se obtuvieron {len(analisis)} carreras desde Firestore.")
    
    # Check Dates
    fechas = sorted(list(set(c['fecha'] for c in analisis)))
    print(f"📅 Fechas Encontradas en Firestore: {fechas}")
    
    if not fechas:
        print("⚠️ No se encontraron fechas.")
        return

    # 2. Inspect Structure (First Race)
    first_race = analisis[0]
    print(f"\n📝 Carrera Muestra: {first_race['hipodromo']} - Carrera {first_race['carrera']}")
    print(f"   📅 Fecha: {first_race['fecha']}")
    print(f"   🕒 Hora: {first_race.get('hora')} (Debe existir)")
    print(f"   🏁 Distancia: {first_race.get('distancia')}")
    
    # 3. Inspect Predictions
    preds = first_race.get('predicciones', [])
    print(f"   🐴 Predicciones: {len(preds)}")
    
    if preds:
        top1 = preds[0]
        print("   🥇 Top 1:")
        print(f"      Nombre: {top1.get('caballo')}")
        print(f"      Jinete: {top1.get('jinete')} (CRÍTICO: Validar que no sea N/A o None)")
        
        jinete = top1.get('jinete')
        if jinete and jinete != 'N/A' and jinete != 'Unknown':
             print(f"✅ Prueba Exitosa: Metadatos (Jinete: {jinete}) servidos desde Firestore.")
        else:
             print("⚠️ Advertencia: Jinete es N/A. La migración podría no haber enriquecido los datos o no hay info en SQLite.")
    else:
        print("⚠️ Carrera sin predicciones.")

if __name__ == "__main__":
    verify_full_cloud()
