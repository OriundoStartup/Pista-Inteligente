
import sys
import os
import pandas as pd
from datetime import datetime

# Add root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.models.data_manager import obtener_analisis_jornada

def verify():
    print("🔬 Verificando Vista Híbrida (Firestore + SQLite)...")
    
    # Force use_firestore=True (Default)
    analisis = obtener_analisis_jornada(use_firestore=True)
    
    if not analisis:
        print("⚠️ No se retornaron análisis. ¿Hay carreras programadas futuras?")
        # Check if local program has dates
        from src.models.data_manager import cargar_programa
        df = cargar_programa(solo_futuras=True)
        if not df.empty:
            print(f"   -> Programa Local tiene: {df['fecha'].unique()}")
        else:
            print("   -> Programa Local está vacío.")
        return

    print(f"✅ Se obtuvieron {len(analisis)} carreras.")
    
    # Check first race
    carrera = analisis[0]
    print("\n📝 Muestra Carrera 1:")
    print(f"   Hipódromo: {carrera.get('hipodromo')}")
    print(f"   Fecha: {carrera.get('fecha')}")
    print(f"   Carrera Nº: {carrera.get('carrera')}")
    
    # Check predictions
    preds = carrera.get('predicciones', [])
    print(f"   Predicciones: {len(preds)}")
    
    if preds:
        top1 = preds[0]
        print("   🥇 Top 1:")
        print(f"      Caballo: {top1.get('caballo')}")
        print(f"      Jinete: {top1.get('jinete')} (Metadata check)")
        print(f"      IA Score: {top1.get('puntaje_ia')} (Firestore check)")
        
        # Verify Source Logic
        # If puntaje_ia is present and matches prob_ml formatting, it likely came from our logic
        if 'puntaje_ia' in top1 and 'jinete' in top1:
             print("\n✅ Integración Exitosa: Datos combinados correctamente.")
             if top1.get('jinete') != 'N/A':
                 print("   -> Metadata (Jinete) encontrada.")
             else:
                 print("   ⚠️ Metadata (Jinete) NO encontrada (Posible desface de programa).")
        else:
             print("\n❌ Error de Integración: Faltan campos clave.")

if __name__ == "__main__":
    verify()
