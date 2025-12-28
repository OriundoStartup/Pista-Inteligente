import firebase_admin
from firebase_admin import credentials, firestore
import sys
import os

# Fix for Windows Unicode
if sys.platform == "win32" and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def verify():
    print("🔍 Verificando datos en Firestore (predicciones)...")
    
    # Auth Logic: Try serviceAccountKey first as it's reliable in this workspace, then ADC
    try:
        if not firebase_admin._apps:
            if os.path.exists('serviceAccountKey.json'):
                print("🔑 Usando serviceAccountKey.json")
                cred = credentials.Certificate('serviceAccountKey.json')
                firebase_admin.initialize_app(cred)
            else:
                print("🔑 Usando Application Default Credentials")
                cred = credentials.ApplicationDefault()
                firebase_admin.initialize_app(cred, {'projectId': 'pista-inteligente'})
    except Exception as e:
        print(f"❌ Auth init failed: {e}")
        return

    try:
        db = firestore.client()
        
        # Reference collection
        collection_ref = db.collection('predicciones')
        
        # Simple count (stream)
        docs = list(collection_ref.stream())
        
        count = len(docs)
        print(f"📊 Total de predicciones encontradas: {count}")
        
        if count > 0:
            # Sort by ID descending (YYYY-MM-DD...) to get newest dates
            docs.sort(key=lambda x: x.id, reverse=True)
            
            latest = docs[0]
            print(f"\n📝 Último documento ID: {latest.id}")
            data = latest.to_dict()
            print("   Contenido (Muestra):")
            print(f"   - Fecha: {data.get('fecha')}")
            print(f"   - Hipódromo: {data.get('hipodromo')}")
            print(f"   - Carrera: {data.get('carrera')}")
            
            detalles = data.get('detalles', [])
            print(f"   - Participantes: {len(detalles)}")
            if detalles:
                # Sort details by propability just in case
                detalles.sort(key=lambda x: x.get('probabilidad', 0), reverse=True)
                print("   - Top 3 Predicciones:")
                for p in detalles[:3]:
                    print(f"     🥇 {p.get('caballo')} -> {p.get('probabilidad')}%")
        else:
            print("⚠️ La colección 'predicciones' está vacía.")
            
    except Exception as e:
        print(f"❌ Error leyendo Firestore: {e}")

if __name__ == "__main__":
    verify()
